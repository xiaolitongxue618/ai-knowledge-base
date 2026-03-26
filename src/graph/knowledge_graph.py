"""
知识图谱模块
基于 NetworkX 和 LLM 的实体关系抽取与可视化
"""

import json
import re
from typing import List, Dict, Any
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import streamlit as st
import subprocess
import sys


def check_and_install_chinese_font():
    """检查并安装中文字体（仅Linux）"""
    if platform.system() != 'Linux':
        return

    # 检查是否已有中文字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    chinese_fonts = ['SimHei', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'WQY-ZenHei']

    has_chinese = any(font in available_fonts for font in chinese_fonts)

    if not has_chinese:
        try:
            print("[INFO] 正在安装中文字体...")
            # 安装fonts-wqy-microhei（包含文泉驿微米黑）
            subprocess.run(
                ['sudo', 'apt-get', 'install', '-y', 'fonts-wqy-microhei'],
                check=False,
                capture_output=True
            )
            # 刷新字体缓存
            subprocess.run(
                ['fc-cache', '-fv'],
                check=False,
                capture_output=True
            )
            print("[INFO] 中文字体安装完成")
        except Exception as e:
            print(f"[WARNING] 无法安装中文字体: {str(e)}")
            print("[INFO] 图谱中文可能显示为方框")


class KnowledgeGraph:
    """知识图谱类"""

    def __init__(self, llm_client):
        """
        初始化知识图谱

        Args:
            llm_client: LLM客户端（OllamaClient实例）
        """
        self.llm_client = llm_client
        self.graph = nx.DiGraph()

    def extract_entities_and_relations(self, text: str, max_entities: int = 15) -> Dict[str, Any]:
        """
        使用LLM从文本中抽取实体和关系

        Args:
            text: 输入文本
            max_entities: 最大实体数量

        Returns:
            包含实体和关系的字典
        """
        # 限制文本长度，避免超过LLM上下文
        if len(text) > 2000:
            text = text[:2000]

        # 使用变量避免f-string格式化冲突
        num_entities = max_entities

        prompt = f"""请从以下文本中提取实体和它们之间的关系。

【文本内容】
{text}

【输出格式】
请以JSON格式返回，包含两个字段：
- entities: 实体列表，每个实体包含name（名称）和type（类型）
- relations: 关系列表，每个关系包含source（源实体）、target（目标实体）和relation（关系描述）

【实体类型】
人物、地点、组织、概念、时间、产品、技术等

【关系类型】
创立、位于、属于、使用、生产、包含、相关、拥有、开发、发布等

【要求】
1. 最多提取 {num_entities} 个实体
2. 关系描述1-4个字
3. 实体之间要有明确的关系
4. 只返回JSON，不要其他解释

请开始分析："""

        try:
            # 调用LLM
            response = self.llm_client.client.generate(
                model=self.llm_client.model,
                prompt=prompt
            )

            result_text = response['response']

            print(f"[DEBUG] LLM原始响应长度: {len(result_text)} 字符")
            print(f"[DEBUG] LLM原始响应前200字符: {result_text[:200]}")

            # 清理JSON字符串
            result_text = result_text.strip()
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
                print(f"[DEBUG] 移除json标记后: {len(result_text)} 字符")
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
                print(f"[DEBUG] 移除代码标记后: {len(result_text)} 字符")

            # 解析JSON
            print(f"[DEBUG] 尝试解析JSON...")
            result = json.loads(result_text)

            # 验证格式
            if 'entities' not in result:
                print(f"[WARNING] JSON缺少entities字段，返回空结果")
                return {'entities': [], 'relations': []}

            if 'relations' not in result:
                print(f"[WARNING] JSON缺少relations字段，设为空列表")
                result['relations'] = []

            # 确保entities和relations是列表
            if not isinstance(result['entities'], list):
                print(f"[WARNING] entities不是列表，转换为空列表")
                result['entities'] = []

            if not isinstance(result['relations'], list):
                print(f"[WARNING] relations不是列表，转换为空列表")
                result['relations'] = []

            print(f"[DEBUG] JSON解析成功:")
            print(f"  - 实体数: {len(result['entities'])}")
            print(f"  - 关系数: {len(result['relations'])}")

            return result

        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON解析失败: {str(e)}")
            print(f"[ERROR] 响应内容: {result_text[:500]}")
            st.warning(f"⚠️ JSON解析失败，LLM返回格式不正确")
            return {'entities': [], 'relations': []}

        except Exception as e:
            print(f"[ERROR] 实体抽取异常: {str(e)}")
            import traceback
            print(f"[ERROR] 详细错误: {traceback.format_exc()}")
            st.warning(f"⚠️ 实体抽取失败: {str(e)}")
            return {'entities': [], 'relations': []}

    def build_graph(self, entities: List[Dict], relations: List[Dict]) -> nx.DiGraph:
        """
        构建NetworkX图谱

        Args:
            entities: 实体列表
            relations: 关系列表

        Returns:
            NetworkX图对象
        """
        G = nx.DiGraph()

        # 添加实体节点
        for entity in entities:
            # 确保entity是字典类型
            if not isinstance(entity, dict):
                print(f"[WARNING] 跳过无效实体（非字典类型）: {entity}")
                continue

            if 'name' not in entity:
                print(f"[WARNING] 跳过无效实体（缺少name字段）: {entity}")
                continue

            G.add_node(
                entity['name'],
                type=entity.get('type', '未知'),
                size=3000
            )

        # 添加关系边
        for rel in relations:
            # 确保rel是字典类型
            if not isinstance(rel, dict):
                print(f"[WARNING] 跳过无效关系（非字典类型）: {rel}")
                continue

            if 'source' not in rel or 'target' not in rel:
                print(f"[WARNING] 跳过无效关系（缺少source或target）: {rel}")
                continue

            source = rel['source']
            target = rel['target']
            relation = rel.get('relation', '相关')

            # 确保节点存在
            if source in G.nodes and target in G.nodes:
                G.add_edge(source, target, relation=relation)
            else:
                print(f"[WARNING] 跳过关系（节点不存在）: {source} -> {target}")

        return G

    def visualize_graph(self, G: nx.DiGraph, title: str = "知识图谱"):
        """
        可视化图谱

        Args:
            G: NetworkX图对象
            title: 图谱标题
        """
        if G.number_of_nodes() == 0:
            st.info("📊 暂无图谱数据")
            return

        # 创建图形
        plt.figure(figsize=(14, 10))

        # 使用spring布局
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

        # 绘制节点
        node_colors = []
        for node in G.nodes():
            node_type = G.nodes[node].get('type', '未知')
            if node_type == '人物':
                node_colors.append('#FF6B6B')
            elif node_type == '地点':
                node_colors.append('#4ECDC4')
            elif node_type == '组织':
                node_colors.append('#45B7D1')
            elif node_type == '概念':
                node_colors.append('#96CEB4')
            elif node_type == '时间':
                node_colors.append('#FFEAA7')
            else:
                node_colors.append('#DDA0DD')

        # 绘制节点
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=3000,
            alpha=0.9,
            edgecolors='white',
            linewidths=2
        )

        # 绘制边
        nx.draw_networkx_edges(
            G, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            alpha=0.6,
            width=1.5
        )

        # 绘制节点标签（中文实体名，英文类型图标）
        for node, (x, y) in pos.items():
            node_type = G.nodes[node].get('type', '未知')

            # 类型图标映射
            type_emoji = {
                '人物': '👤',
                '地点': '📍',
                '组织': '🏢',
                '概念': '💡',
                '时间': '🕐',
                '产品': '📦',
                '技术': '⚙️',
                '未知': '❓'
            }

            emoji = type_emoji.get(node_type, '📌')

            # 显示：emoji + 节点名
            label_text = f"{emoji}\n{node}"
            plt.text(x, y, label_text, fontsize=10, fontweight='bold',
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                              edgecolor='gray', alpha=0.9))

        # 绘制边标签（关系）
        edge_labels = nx.get_edge_attributes(G, 'relation')
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels,
            font_size=9,
            bbox=dict(
                boxstyle='round,pad=0.3',
                facecolor='#FFFACD',
                edgecolor='gray',
                alpha=0.8
            )
        )

        # 添加标题
        plt.title(title, fontsize=18, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()

        # 显示图表
        st.pyplot(plt)
        plt.close()

    def get_graph_statistics(self, G: nx.DiGraph) -> Dict[str, Any]:
        """
        获取图谱统计信息

        Args:
            G: NetworkX图对象

        Returns:
            统计信息字典
        """
        stats = {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': nx.density(G),
            'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
        }

        # 实体类型统计
        entity_types = {}
        for node in G.nodes():
            node_type = G.nodes[node].get('type', '未知')
            entity_types[node_type] = entity_types.get(node_type, 0) + 1

        stats['entity_types'] = entity_types

        return stats

    def generate_from_documents(self, documents: List[Any], max_docs: int = 5) -> nx.DiGraph:
        """
        从文档列表生成知识图谱

        Args:
            documents: 文档列表
            max_docs: 最大处理文档数

        Returns:
            NetworkX图对象
        """
        all_entities = []
        all_relations = []
        entity_names = set()

        # 处理每个文档
        for i, doc in enumerate(documents[:max_docs]):
            try:
                print(f"[DEBUG] 开始处理文档 {i+1}/{min(len(documents), max_docs)}: {doc.file_name}")

                # 读取文档内容
                print(f"[DEBUG] 读取文件: {doc.file_path}")
                with open(doc.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                print(f"[DEBUG] 文档内容长度: {len(content)} 字符")

                # 抽取实体和关系
                print(f"[DEBUG] 开始调用LLM抽取实体和关系...")
                result = self.extract_entities_and_relations(content)

                print(f"[DEBUG] LLM返回结果:")
                print(f"  - 实体数量: {len(result.get('entities', []))}")
                print(f"  - 关系数量: {len(result.get('relations', []))}")

                # 显示抽取的实体
                entities = result.get('entities', [])
                if entities:
                    print(f"[DEBUG] 抽取到的实体（前3个）:")
                    for entity in entities[:3]:
                        if isinstance(entity, dict):
                            print(f"    - {entity.get('name', '未知')} ({entity.get('type', '未知')})")
                        else:
                            print(f"    - {entity} (类型: {type(entity)})")

                # 去重实体
                valid_entities = []
                for entity in entities:
                    if not isinstance(entity, dict):
                        print(f"[WARNING] 跳过非字典实体: {entity}")
                        continue

                    if 'name' not in entity:
                        print(f"[WARNING] 跳过无名字实体: {entity}")
                        continue

                    if entity['name'] not in entity_names:
                        valid_entities.append(entity)
                        entity_names.add(entity['name'])

                all_entities.extend(valid_entities)

                # 验证并添加关系
                relations = result.get('relations', [])
                valid_relations = []
                for rel in relations:
                    if not isinstance(rel, dict):
                        print(f"[WARNING] 跳过非字典关系: {rel}")
                        continue

                    if 'source' not in rel or 'target' not in rel:
                        print(f"[WARNING] 跳过不完整关系: {rel}")
                        continue

                    valid_relations.append(rel)

                all_relations.extend(valid_relations)

                print(f"[DEBUG] 本轮处理完成: 有效实体 {len(valid_entities)} 个, 有效关系 {len(valid_relations)} 个")

                print(f"[DEBUG] 文档 {i+1} 处理完成")

            except Exception as e:
                print(f"[ERROR] 处理文档 {doc.file_name} 失败: {str(e)}")
                import traceback
                print(f"[ERROR] 详细错误: {traceback.format_exc()}")
                continue

        print(f"[DEBUG] 所有文档处理完成")
        print(f"[DEBUG] 总实体数: {len(all_entities)}")
        print(f"[DEBUG] 总关系数: {len(all_relations)}")

        # 构建图谱
        print(f"[DEBUG] 开始构建NetworkX图谱...")
        G = self.build_graph(all_entities, all_relations)

        print(f"[DEBUG] 图谱构建完成")
        print(f"[DEBUG] 节点数: {G.number_of_nodes()}")
        print(f"[DEBUG] 边数: {G.number_of_edges()}")

        return G

    def export_graph_data(self, G: nx.DiGraph) -> str:
        """
        导出图谱数据为JSON格式

        Args:
            G: NetworkX图对象

        Returns:
            JSON字符串
        """
        export_data = {
            'nodes': [],
            'edges': []
        }

        # 导出节点
        for node in G.nodes():
            export_data['nodes'].append({
                'name': node,
                'type': G.nodes[node].get('type', '未知')
            })

        # 导出边
        for source, target, edge_data in G.edges(data=True):
            export_data['edges'].append({
                'source': source,
                'target': target,
                'relation': edge_data.get('relation', '相关')
            })

        return json.dumps(export_data, ensure_ascii=False, indent=2)
