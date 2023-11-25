## Solução por Epsilon Restrito

A solução por epsilon restrito obteve os mesmos resultados do semestre anterior, tendo em visto que temos a mesma base de dados. O hipervolume da solução também não se alterou, mesmo forçando com que sejam geradas soluções com cada valor de custo de manutenção possível.

## Maximizar o Hipervolume

O [[Hipervolume]] é a área encobrida entre o ponto de Nadir e os pontos da fronteira Pareto. Ao que tudo indica o código criado pelo Carrano calcula o Hipervolume (área) normalizando os dados para a escala entre zero e um, com minha solução correspondendo à 0.6287.

- Seria o cálculo do professor um percentual da área do quadrado de lado unitário e vértice na origem?
- Seria possível criar um modelo de otimização que gere K soluções e tenha objetivo maximizar o hipervolume? Aparentemente sim!

- [ ] Realizar modelagem do hipervolume como função linear de duas funções objetivo, dado um determinado ponto de Nadir.
- [ ] Implementar alteração
- [ ] Maximizar hipervolume

### Modelagem Atual
Minimizar a função de falha $f_f$, considerando um custo de manutenção $f_m$ constante.
$$ \min_x \quad F = f_f(x) $$ $$fm(x) = \epsilon $$
$$ \sum_{j=1}^{M} x_{ij} = 1;\quad i \in \{1,.., N\} $$
$$ x∈ \{0, 1\} $$

### Modelagem alternativa
Maximizar o hipervolume normalizado para a solução num espaço unitário entre os pontos utópico $u=[u_m, u_f] = [f_m(x^*), f_f(x^*)]$ e de nadir $v=[v_m, v_f] = [\max_x\; f_m(x), \max_x\; f_f(x)]$.

![[Recursos/hipervolume_2d.png]]

Sejam $h_k$ a altura e $b_k$ a base do retângulo que determina a contribuição da solução $k$ para o hipervolume. Podemos escrevê-los em função dos valores das funções objetivo, conforme:

$h_k=\hat{f_f}(X_{k-1}^*)-\hat{f_f}(X_k^*)$
$=\frac{f_f(X_{k-1}^*) - u_f}{ v_f - u_f} -  \frac{f_f(X_k^*) - u_f}{ v_f - u_f }$
$=\frac{f_f(X_{k-1}^*) - f_f(X_k^*)}{ v_f - u_f }$

$b_k = 1-\hat{f_m}(X_k^*)$
$=1-\frac{f_m(X_k^*)-u_m}{v_m-u_m}$

Podemos escrever o novo objetivo como:
$$ max \quad G = \sum_{k=1}^{K}{ h_k b_k } $$
Sujeito à:
$$b_k=1-\frac{f_m(X_k^*)-u_m}{v_m-u_m}; \quad \forall k \in \{1,...,K\}$$
$$h_k=\frac{f_f(X_{k-1}^*) - f_f(X_k^*)}{ v_f - u_f }; \quad \forall k \in \{1,...,K\}$$
$$f_m(X_k) = k; \quad \forall k \in \{1,...,K\}$$
$$ \sum_{j=1}^{M} x_{kij} = 1;\quad \forall i \in \{1,.., N\},\; \forall k \in \{1,...,K\} $$
$$ x_{kij}∈ \{0, 1\} $$
