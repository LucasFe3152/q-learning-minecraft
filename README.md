# Q-Learning: Mineração Autônoma em 2D

**Equipe:**
- Gustavo Caldas
- José Gabriel  
- Lucas Feitosa
- Ricardo Nabuco
- Vinicius Vasconi

**Demonstração:** [[Hugging Face Spaces](https://huggingface.co/spaces/LucasFe0162/Q-learning-mineracao-minecraft)]  

---

## Sobre o Projeto

Este projeto é uma demonstração interativa do algoritmo de Aprendizado por Reforço **Q-Learning** aplicado a um ambiente de mineração em grid 2D. O objetivo é treinar um agente autônomo para coletar todos os minérios valiosos espalhados pelo mapa da forma mais eficiente possível, evitando rotas vazias e obstáculos.

### Destaques da Implementação

* **Construído do Zero:** Todo o núcleo de inteligência do agente (como a Política Épsilon-Gulosa, a Equação de Bellman e a atualização da Tabela Q) foi desenvolvido em **Python puro**. Nenhuma biblioteca externa de Machine Learning ou de manipulação de matrizes foi utilizada para a lógica da IA.
* **Mapeamento Universal:** O agente não apenas "decora" um único caminho. Durante o treinamento, ele é exposto a posições aleatórias (*Random Starts*), o que garante que ele aprenda a se locomover e encontrar a rota ótima **começando de absolutamente qualquer lugar do mapa**.

---

## Como Executar Localmente

O projeto utiliza o **Streamlit** exclusivamente para a renderização da interface gráfica. Para rodar a simulação na sua própria máquina, siga os passos abaixo:

1. Certifique-se de ter o Python instalado.
2. Instale o Streamlit (única dependência do projeto):
   ```bash
   pip install streamlit