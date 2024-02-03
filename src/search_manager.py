from node import Node


class SearchManager:
    def __init__(self, initial_node: Node):
        # The list of nodes contains all nodes that were ever generated (without duplicates),
        # node are never removed from there.
        initial_node.isInOpenList = True
        self.GeneratedUniqueNodesList = [initial_node]
        # The dictionary maps each state to the index of its corresponding node in GeneratedUniqueNodesList
        # (which always remains constant).
        self.StateToIndexMapping = dict({str(initial_node.state): 0})
        # The heap that contains indexes of nodes in L, sorted by their corresponding f-value.
        # The open list is a heap queue.
        # https://docs.python.org/3/library/heapq.html
        self.OpenList = list()
        self.numOfNodesInOpenList = 0
        self.numOfUniqueGeneratedNodes = 1
        heappush(self, 0)

    def GetCurrentNode(self):
        current_node_index = heappop(self)
        self.GeneratedUniqueNodesList[current_node_index].isInOpenList = False
        self.GeneratedUniqueNodesList[current_node_index].indexInOpenList = -1
        return self.GeneratedUniqueNodesList[current_node_index]
        
    def ChildrenHandler(self, child: Node):
        # The cost of the path to child through current
        child_key = str(child.state)
        duplicate_index = self.StateToIndexMapping.get(child_key)
        # No duplication => The first node which corresponds to child's state
        # The node is added to the end of GeneratedUniqueNodesList with the corresponding pair
        # added to StateToIndexMapping
        # The node is then added to the open list
        if duplicate_index is None:
            child.isInOpenList = True
            self.StateToIndexMapping[child_key] = self.numOfUniqueGeneratedNodes
            self.GeneratedUniqueNodesList.append(child)
            heappush(self, self.numOfUniqueGeneratedNodes)
            # self.GeneratedUniqueNodesList[-1].indexInOpenList = self.OpenList.index(self.numOfGeneratedNode )
            self.numOfUniqueGeneratedNodes += 1
          
        # Duplicate detection => Verify whether this is the cheapest path to the state or not
        else:
            duplicate = self.GeneratedUniqueNodesList[duplicate_index]
            duplicate_status = duplicate.isInOpenList
            # If this condition does not hold ==>
            # The duplicate represents a more expansive path and nothing more can be done.
            if child.g_value() < duplicate.g_value():
                # child's cost is the cheapest (cheaper than the duplicate's)
                # child will be added to the open list in any case.
                child.isInOpenList = True
                # Replace the duplicate with child
                self.GeneratedUniqueNodesList[duplicate_index] = child
                if duplicate_status:
                    # Duplicate was in the open list => Update the priority queue according to the child's f-value
                    heapify(self)
                else:
                    # Duplicate was not in the open list => Add the child to the open list
                    # (the node's state is re-added to the open list)
                    heappush(self, duplicate_index) 
                # self.GeneratedUniqueNodesList[duplicate_index].indexInOpenList = self.OpenList.index(duplicate_index)
         

# The following depends on 'node' class definition of :
    # def __lt__(self, other):
    #     return (self.f_value()) < (other.f_value())
            
                   
def heappush(search_manager: SearchManager, index):
    """Push item onto heap, maintaining the heap invariant."""
    search_manager.OpenList.append(index)
    search_manager.numOfNodesInOpenList += 1
    # print("Push: ",len(SearchManager.OpenList),SearchManager.numOfNodesInOpenList,flush=True)
    _siftdown(search_manager, 0, search_manager.numOfNodesInOpenList-1)


def heappop(search_manager: SearchManager):
    """Pop the smallest item off the heap, maintaining the heap invariant."""
    lastelt = search_manager.OpenList.pop()    # raises appropriate IndexError if heap is empty
    search_manager.numOfNodesInOpenList = search_manager.numOfNodesInOpenList - 1
    if search_manager.OpenList:
        returnitem = search_manager.OpenList[0]
        search_manager.OpenList[0] = lastelt
        _siftup(search_manager, 0)
        return returnitem
    return lastelt


def heapify(search_manager: SearchManager):
    """Transform list into a heap, in-place, in O(len(x)) time."""
    n = search_manager.numOfNodesInOpenList
    # Transform bottom-up.  The largest index there's any point to looking at
    # is the largest with a child index in-range, so must have 2*i + 1 < n,
    # or i < (n-1)/2.  If n is even = 2*j, this is (2*j-1)/2 = j-1/2 so
    # j-1 is the largest, which is n//2 - 1.  If n is odd = 2*j+1, this is
    # (2*j+1-1)/2 = j so j-1 is the largest, and that's again n//2-1.
    for i in reversed(range(n//2)):
        _siftup(search_manager, i)


def _siftup(search_manager: SearchManager, pos):
    endpos = search_manager.numOfNodesInOpenList
    startpos = pos
    newitem = search_manager.OpenList[pos]
    # Bubble up the smaller child until hitting a leaf.
    childpos = 2*pos + 1    # leftmost child position
    while childpos < endpos:
        # Set childpos to index of smaller child.
        rightpos = childpos + 1
        if rightpos < endpos and not search_manager.GeneratedUniqueNodesList[search_manager.OpenList[childpos]] < search_manager.GeneratedUniqueNodesList[search_manager.OpenList[rightpos]]:
            childpos = rightpos
        # Move the smaller child up.
        search_manager.OpenList[pos] = search_manager.OpenList[childpos]
        pos = childpos
        childpos = 2*pos + 1
    # The leaf at pos is empty now.  Put newitem there, and bubble it up
    # to its final resting place (by sifting its parents down).
    search_manager.OpenList[pos] = newitem
    _siftdown(search_manager, startpos, pos)


# 'heap' is a heap at all indices >= startpos, except possibly for pos.  pos
# is the index of a leaf with a possibly out-of-order value.  Restore the
# heap invariant.
def _siftdown(search_manager: SearchManager, startpos, pos):
    newitem = search_manager.OpenList[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    while pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = search_manager.OpenList[parentpos]
        if search_manager.GeneratedUniqueNodesList[newitem] < search_manager.GeneratedUniqueNodesList[parent]:
            search_manager.OpenList[pos] = parent
            pos = parentpos
            continue
        break
    search_manager.OpenList[pos] = newitem
