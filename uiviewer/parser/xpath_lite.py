# -*- coding: utf-8 -*-

from typing import Dict


class XPathLiteGenerator:
    def __init__(self, platform: str, treedata: Dict):
        """
        Initializes the XPathLiteGenerator class.

        Args:
        platform (str): The platform type (e.g., 'ios', 'android').
        treedata (Dict): The JSON tree structure data.

        Returns:
        None
        """
        self.platform = platform
        self.treedata = treedata
        self.node_map = self._build_node_map(treedata)

    def _build_node_map(self, node: Dict, node_map: Dict[str, Dict] = None) -> Dict[str, Dict]:
        """
        Builds a node map for quick lookup by node _id.

        Args:
        node (Dict): The current node.
        node_map (Dict[str, Dict], optional): The node map. Default is an empty dictionary.

        Returns:
        Dict[str, Dict]: The node map.
        """
        if node_map is None:
            node_map = {}
        node_map[node["_id"]] = node
        if "children" in node:
            for child in node["children"]:
                self._build_node_map(child, node_map)
        return node_map

    def _find_node_by_id(self, target_id: str) -> Dict:
        """
        Finds a node by its ID.

        Args:
        target_id (str): The target node ID.

        Returns:
        Dict: The target node.
        """
        return self.node_map.get(target_id)

    def _get_value(self, node: Dict) -> str:
        """
        Gets the specific attribute value of a node to generate part of the XPath expression.

        Args:
        node (Dict): The current node.

        Returns:
        str: Part of the XPath expression.
        """
        if node.get("resourceId"):
            return f'//*[@resource-id="{node["resourceId"]}"]'
        elif node.get("text"):
            return f'//*[@text="{node["text"]}"]'
        elif node.get("description"):
            return f'//*[@content-desc="{node["description"]}"]'
        elif node.get("label"):
            return f'//*[@label="{node["label"]}"]'
        elif node.get("name"):
            return f'//*[@name="{node["name"]}"]'
        elif node.get("id"):   # harmonyos, ios
            return f'//*[@id="{node["id"]}"]'
        return None

    def _build_xpath(self, node: Dict, path: str, found_value: bool = False) -> str:
        """
        Recursively builds the XPath expression.

        Args:
        node (Dict): The current node.
        path (str): The current path.
        found_value (bool, optional): Whether a specific attribute value has been found. Default is False.

        Returns:
        str: The complete XPath expression.
        """
        if not node:
            return path
        value = self._get_value(node)
        if value:
            found_value = True
            return value + path
        if self.platform == 'ios' and not (node.get("lable") or node.get("name")):
            # If the platform is iOS and the node does not have lable, name, build from root
            return self._build_from_root(node, path)

        parent_node = self._find_node_by_id(node["_parentId"])
        if parent_node:
            siblings = parent_node.get("children", [])
            index = 1
            for sibling in siblings:
                if sibling["_type"] == node["_type"]:
                    if sibling["_id"] == node["_id"]:
                        break
                    index += 1
            path = f'/{node["_type"]}[{index}]' + path
            return self._build_xpath(parent_node, path, found_value)
        return path

    def _build_from_root(self, node: Dict, path: str) -> str:
        """
        Builds the XPath expression from the root node.

        Args:
        node (Dict): The current node.
        path (str): The current path.

        Returns:
        str: The complete XPath expression.
        """
        if "_type" in node:
            parent_node = self._find_node_by_id(node["_parentId"])
            if parent_node:
                siblings = parent_node.get("children", [])
                index = 1
                for sibling in siblings:
                    if sibling["_type"] == node["_type"]:
                        if sibling["_id"] == node["_id"]:
                            break
                        index += 1
                path = f'/{node["_type"]}[{index}]' + path
                return self._build_from_root(parent_node, path)
        return '//' + path.lstrip('/')

    def get_xpathLite(self, target_id: str) -> str:
        """
        Gets the XPathLite path for the target node.

        Args:
        target_id (str): The target node ID.

        Returns:
        str: The XPathLite path.
        """
        target_node = self._find_node_by_id(target_id)
        if not target_node:
            return None

        xpath_lite = self._build_xpath(target_node, "")
        if not xpath_lite.startswith('//*[@'):
            xpath_lite = self._build_from_root(target_node, "")

        return xpath_lite