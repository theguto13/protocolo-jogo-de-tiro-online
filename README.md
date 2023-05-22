# Protocolo de Jogo de Tiro Online (Python)
Protocolo de um jogo de tiro online. Atividade realizada em grupo: Augusto Júnior; Larissa Lanzana; Renata Rocha; Yasmin Prichoa


## Instalação

Para o protocolo funcionar corretamente, você deve ter instalado em seu Python a biblioteca **pygame**. Para instalá-la, é bem simples: basta executar o código abaixo no terminal do Windows:

```
pip install pygame
```

Após efetuar a instalação do **pygame**, você deve ter baixado em seu computador o arquivo ***client.py*** e ao menos um computador precisa ter o ***server.py*** baixado. Esse computador será o servidor do jogo online. Para jogar com outro computador, desde que ele esteja na mesma rede que você, basta colocar o IP dele no campo **'HOST'** do ***cliente.py*** e executá-lo, usando Python3.

É importante ressaltar que, se for utilizado o mesmo computador para hostear e jogar, o arquivo ***server.py*** deve ser executado primeiro. Além disso, no ***client.py*** do computador do servidor, não é necessário colocar o IP, já que a própria máquina está hosteando.
