# utils/doubly_linked_list.py

class DoublyLinkedListNode:
    def __init__(self, node):
        self.node = node
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self) -> None:
        self.head = None
        self.tail = None

    def append(self, node):
        new_node = DoublyLinkedListNode(node)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def remove(self, node):
        current = self.head
        while current is not None:
            if current.node == node:
                if current.prev is not None:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next is not None:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                break
            current = current.next