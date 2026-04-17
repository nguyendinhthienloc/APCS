#include <iostream>
struct Node {
    int data;
    Node* pNext;
    Node(int data, Node* pNext) : data(data), pNext(pNext) {} //constructor for quick node creation
};
struct List {
    Node* pHead;
};

void moveOddLeftEvenRight(List& l) {
if (l.pHead == nullptr) return;

    Node* cur = l.pHead;
    Node* pHeadOdd = nullptr;
    Node* pHeadEven = nullptr;
    Node* cur1 = nullptr; //odd
    Node* cur2 = nullptr; //even
    while (cur != nullptr){
        if (cur -> data % 2 == 0){
            if (pHeadEven == nullptr){
                pHeadEven = cur;
                cur2 = cur;
            }
            else{
                cur2 -> pNext = cur;
                cur2 = cur;
            }
        }
        else if (cur -> data % 2 != 0){
            if (pHeadOdd == nullptr){
                pHeadOdd = cur;
                cur1 = cur;
            }
            else{
                cur1 -> pNext = cur;
                cur1= cur;
            }
        }
        cur = cur -> pNext;
    }
    if (pHeadOdd == nullptr || pHeadEven == nullptr){
        return;
    }
    else{
        l.pHead = pHeadOdd;
        cur1 -> pNext = pHeadEven;
        cur2 -> pNext = nullptr;
    }
}
int main() {
    //Test with 1 -> 2 -> 3 -> 4 -> 5 -> nullptr
    Node* n1 = new Node{1, nullptr};
    //Node* n2 = new Node{2, nullptr};
    Node* n3 = new Node{3, nullptr};
    //Node* n4 = new Node{4, nullptr};
    Node* n5 = new Node{5, nullptr}; //tail has set to nullptr
    //n1->pNext = n2;
    //n2->pNext = n3;
    //n3->pNext = n4;
    //n4->pNext = n5;
    n1->pNext = n3;
    n3->pNext = n5;
    List l;
    l.pHead = n1;
    moveOddLeftEvenRight(l);
    // Print the modified list
    Node* cur = l.pHead;
    while (cur != nullptr) {
        std::cout << cur->data << " ";
        cur = cur->pNext;
    }
    std::cout << std::endl;
    return 0;
    
}
