class HeapElement {
    constructor(data, priority) {
        this.data = data;
        this.priority = priority;
    }
}

class MinHeap {
    constructor() {
        this.data = [];
        this.size = 0;
    }

    static parent(index) {
        return ~~((index-1)/2);
    }

    static first_child(index) {
        return index*2+1;
    }

    fix_element(pos) {
        let par = MinHeap.parent(pos);

        while (pos > 0 && this.data[pos].priority < this.data[par].priority) {
            [this.data[pos],this.data[par]] = [this.data[par],this.data[pos]];
            pos = par;
            par = MinHeap.parent(pos);
        }
    }

    new_priority(node,priority) {
        for (let i=0; i<this.size; i++) {
            if (this.data[i].data == node) {
                this.data[i].priority = priority;
            }
            this.fix_element(i);
            return;
        }
    }

    add_element(node,priority) {
        this.data[this.size] = new HeapElement(node,priority);

        this.fix_element(this.size);
        this.size += 1;
    }

    get_min() {
        let out = this.data[0];
        this.size -= 1;
        this.data[0] = this.data[this.size];

        let pos = 0;
        let left = 1;
        let right = 2;
        while (left < this.size) {
            if (this.data[left].priority < this.data[pos].priority) {
                if (!(right < this.size) || (this.data[left].priority <= this.data[right].priority)) {
                    [this.data[pos],this.data[left]] = [this.data[left],this.data[pos]];
                    pos = left;
                    left = MinHeap.first_child(pos);
                    right = left+1;
                } else {
                    [this.data[pos],this.data[right]] = [this.data[right],this.data[pos]];
                    pos = right;
                    left = MinHeap.first_child(pos);
                    right = left+1;
                }
            } else if (right < this.size) {
                if (this.data[right].priority < this.data[pos].priority) {
                    [this.data[pos],this.data[right]] = [this.data[right],this.data[pos]];
                    pos = right;
                    left = MinHeap.first_child(pos);
                    right = left+1;
                } else {
                    break
                }
            } else {
                break;
            }
        }

        return out.data;
    }
}

function l2_distance(x1,y1,z1,x2,y2,z2) {
    return Math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2);
}

function compute_h(nodes, end) {
    let h = [];
    for (let i=0; i<nodes.length; i++) {
        h[i] = Math.abs(nodes[i].x-nodes[end].x)+Math.abs(nodes[i].y-nodes[end].y)+Math.abs(nodes[i].z-nodes[end].z);
    }
    return h;
}

function get_xyz(node) {
    return [node.x,node.y,node.z];
}

function reconstruct_path(previous, node, nodes) {
    for (let i=0; i<nodes.length; i++) {
        console.log(previous[i]);
    }
    let path = [get_xyz(nodes[node])];
    let next = previous[node];
    while (next != -1) {
        path.splice(0,0,get_xyz(nodes[next]));
        next = previous[next];
    }
    return path;
}

function a_star(nodes, edges, start, end) {
    if (start == -1 || end == -1) {
        return -1;
    }

    let open_set = new MinHeap();
    open_set.add_element(start,0);

    let previous = new Map();
    previous[start] = -1;

    let g = new Map();
    for (let i=0; i<nodes.length; i++) {
        g[i] = Number.POSITIVE_INFINITY;
    }
    g[start] = 0;

    let h = compute_h(nodes, end);

    while (open_set.size > 0) {
        let node = open_set.get_min();
        if (node == end) {
            return reconstruct_path(previous, end, nodes);
        }

        for (let i=0; i<edges[node].length; i++) {
            let neighbor = edges[node][i];
            let gScore = g[node] + l2_distance(nodes[node].x,nodes[node].y,nodes[node].z,nodes[neighbor].x,nodes[neighbor].y,nodes[neighbor].z);
            
            if (gScore < g[neighbor]) {
                previous[neighbor] = node;
                g[neighbor] = gScore;
                if (neighbor in open_set.data) {
                    open_set.new_priority(neighbor,gScore+h[neighbor]);
                } else {
                    open_set.add_element(neighbor,gScore+h[neighbor]);
                }
            }
        }
    }

    return -1;
}

const n1 = {
    name: "a",
    x: 0,
    y: 0
};

const n2 = {
    name: "b",
    x: 0,
    y: -1
};

const n3 = {
    name: "c",
    x: 1,
    y: 0
};

const n4 = {
    name: "d",
    x: 1,
    y: 1
};

const n5 = {
    name: "e",
    x: 3,
    y: 3
};

//console.log(a_star([n1,n2,n3,n4,n5],[[1,2],[0,4],[0,3],[2,1],[1]],0,4))

export {a_star};
