"""
知识图谱模块
基于 NetworkX 和 LLM 的实体关系抽取与可视化
"""

import json
import re
from typing import List, Dict, Any
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.font_manager import FontProperties
import streamlit as st


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

        prompt = f"""请从以下文本中提取实体和它们之间的关系。

文本：
{text}

请以JSON格式返回，格式如下：
{{
  "entities": [
    {{"name": "实体名称", "type": "类型（如：人物、地点、概念、组织等）"}}
  ],
  "relations": [
    {{"source": "实体1", "target": "实体2", "relation": "关系描述"}}
  ]
}

要求：
1. 提取最重要的{max_entities}个实体
2. 实体之间要有明确的关系
3. 关系要简洁（1-4个字）
4. 只返回JSON，不要其他内容

JSON："""

        try:
            # 调用LLM
            response = self.llm_client.client.generate(
                model=self.llm_client.model,
                prompt=prompt
            )

            result_text = response['response']

            # 清理JSON字符串
            result_text = result_text.strip()
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()

            # 解析JSON
            result = json.loads(result_text)

            # 验证格式
            if 'entities' not in result or 'relations' not in result:
                return {'entities': [], 'relations': []}

            return result

        except Exception as e:
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
            G.add_node(
                entity['name'],
                type=entity.get('type', '未知'),
                size=3000
            )

        # 添加关系边
        for rel in relations:
            source = rel['source']
            target = rel['target']
            relation = rel['relation']

            # 确保节点存在
            if source in G.nodes and target in G.nodes:
                G.add_edge(source, target, relation=relation)

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

        # 绘制节点标签
        nx.draw_networkx_labels(
            G, pos,
            font_size=11,
            font_family='sans-serif',
            font_weight='bold',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='white',
                edgecolor='gray',
                alpha=0.9
            )
        )

        # 绘制边标签（关系）
        edge_labels = nx.get_edge_attributes(G, 'relation')
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels,
            font_size=9,
            font_family='sans-serif',
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
            with st.spinner(f"正在分析文档 {i+1}/{min(len(documents), max_docs)}..."):
                try:
                    # 读取文档内容
                    with open(doc.file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 抽取实体和关系
                    result = self.extract_entities_and_relations(content)

                    # 去重实体
                    for entity in result['entities']:
                        if entity['name'] not in entity_names:
                            all_entities.append(entity)
                            entity_names.add(entity['name'])

                    # 添加关系
                    all_relations.extend(result['relations'])

                except Exception as e:
                    st.warning(f"⚠️ 处理文档 {doc.file_name} 失败: {str(e)}")
                    continue

        # 构建图谱
        G = self.build_graph(all_entities, all_relations)

        return G

    def export_graph_data(self, G: nx.DiGraph) -> str:
        """
        导出图谱数据为JSON格式

        Args:
            G: NetworkX图对象

        Returns:
            JSON字符串
        """
        data = {
            'nodes': [],
            'edges': []
        }

        # 导出节点
        for node in G.nodes():
            data['nodes'].append({
                'name': node,
                'type': G.nodes[node].get('type', '未知')
            })

        # 导出边
        for source, target, data in G.edges(data=True):
            data['edges'].append({
                'source': source,
                'target': target,
                'relation': data.get('relation', '相关')
            })

        return json.dumps(data, ensure_ascii=False, indent=2)
