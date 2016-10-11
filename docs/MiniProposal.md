# Mini-proposal: Inferring Missing Attributes in Online Social Networks

## Scenario
In Online Social Networks, a **community structure** is defined as a set of nodes grouped with internally dense connections from the whole network. That is to say, the probability for two nodes to form a social relation is higher if they are in the same community. The intrinsic reason for the community structure is so-called homophily, which indicates the trend that two similar social actors are more likely to be friends. The common aspects which are shared among nodes in the same community include common friends, or common properties (e.g., profile attributes). Therefore, it is possible to use community structures to infer the missing attributes as long as there exist some kinds of obvious correlations among social actors and attribtues.

## Problem Description
Assume that we have a fully observed social network $G_N=(V_N, E_N)$ where $V_N$ is the social actor set and $E_N$ is the social relation set, and a partially observed actor-attribute bipartite graph $G_A=(V_N+V_A, E_A'), E_A' \subset E_A$ where $V_A$ is the attribute node set, and $E_A$ is the set of all attribute links that really exist while $E_A'$ only contains the observed ones. Given an actor-attribute pair $(v, a) \in V_N \times V_A$, determine whether $(v,a) \in E_A$.

## Modeling
To infer the missing attributes, we first need to build a generative model to abstract the original social network with both stuctural information and profile information taken into consideration. In this step, we want our generative model to generate a new network which approaches the orignal network graph by means of obtaining the parameters (solve an optimization problem). Generally, a generative network model contains a matrix of the probabilities of every two social actors having a social relation.

### Typical Generative Network Models
- **Chung Lu Graph Models (CL)**

Every edge is sampled proportional to the product of the degrees of its endpoints
$$ P_{CL}(e_{i,j} \in E|\Theta_{CL}) = \frac{\theta_{d_i}\theta_{d_j}}{\sum_{v_k \in V}\theta_{d_k}} $$
where $\Theta_{CL}=\\{\theta_{d_1},\ldots, \theta_{d_{|V|}}\\}$ and $\theta_{d_i}=d_i$. The formulation guarantees the expected degree of the sampled graph is equal to the degree of the original graph.

- **Kronecker Product Graph Models (KPGM)**

$K$ Kronecker products of a $b \times b$ initiator matrix of parameter $\Theta_{KP}$ are used to define the marginal probabilities of edges in the network.
$$ P_{KP}(e_{i,j} \in E|\Theta_{KP}) = \prod_{k=1}^{K} \Theta_{KP}(\sigma_{ki},\sigma_{kj}) $$
where $\sigma_{k,i}$ indicates the position of the parameter in the initiator matrix $\Theta_{KP}$ that is associated with $v_i$ in the $k$th Kronecker multiplication.

### Generative Attributed Network Models

- **Atributed Graph Model (AGM)**
If the correlations of attributes are taken into account, the generative model incorporates distributions over both the attribute $P(X|\Theta_X)$ and $P(E|\Theta_M)$.
$$ P(G|X, \Theta_{M}, \Theta_{F}) = \prod_{e_{i,j} \in E} P(e_{i,j}|f(x_i,x_j), \Theta_{M}, \Theta_{F}) $$
$$\begin{eqnarray} 
P_o(e_{i,j}|f(x_i,x_j), \Theta_{M}, \Theta_{F}) &=& P_o(e_{i,j}|\Theta_{M}, \Theta_{F}) \frac{P_o(f(x_i,x_j)|e_{i,j}, \Theta_{M}, \Theta_{F})}{P_o(f(x_i,x_j)|\Theta_{M}, \Theta_{F})} \\\\
&\approx& P_M(e_{i,j}|\Theta_{M}) \frac{P_o(f(x_i,x_j)|e_{i,j}, \Theta_{M}, \Theta_{F})}{P_M(f(x_i,x_j)|e_{i,j},\Theta_{M}, \Theta_{F})}
\end{eqnarray}$$
where $x_i \in X$ (attribute vector/matrix), $f(x_i,x_j)$ is a deterministic function which maps tuples of attribute vectors to a single model of correlation across linked edges.

- **Social Circle Detection** Profile similarity parameter is introduced in this model, with social circle division treated as a latent variable.
$$
P_{SC}(e_{i,j}\in E|\mathcal{C}, \Theta_{SC}) = \frac{e^{\Phi(e_{i,j})}}{1+e^{\Phi(e_{i,j})}}
$$
$$
\Phi(e) = \sum_{C_k \in \mathcal{C}}(\delta(e \in C_k)) - \alpha_k \delta(e \notin C_k) \langle \phi(e), \theta_k \rangle
$$
where $\mathcal{C}$ is the social circle set, $\delta(c)$ is the indicator function, $\alpha_k$ is the pernalizing parameter and $\phi(e)$ is the profile similarity between two ends of the edge.

### Our Model: Generative Social Attribute Network Model
The former models only use the similarity function as conditions. It is difficult to recover the attribute information from this kind of function. That is to say, we need to directly combine the attribute bigraph into conditions.
<div>
$$
P(G_N|G_A, \Theta_N, \Theta_A)=
\prod_{e_{i,j} \in E_N}{P(e_{i,j} \vert \mathcal{A}_{i}, \mathcal{A}_j, \Theta_N, \Theta_A)} \times \prod_{e_{i,j} \not\in E_N}{P(e_{i,j} \vert \mathcal{A}_i,\mathcal{A}_j, \Theta_N, \Theta_A)}
$$
</div>
