import threading
import time
from queue import Queue
import matplotlib.pyplot as plt

class LinhaDeProducao:
    def __init__(self, capacidade_buffer, num_produtores, num_consumidores, timesteps):
        self.buffer = Queue(maxsize=capacidade_buffer)
        self.capacidade_buffer = capacidade_buffer
        self.timesteps = timesteps
        self.sem_espacos = threading.Semaphore(capacidade_buffer)
        self.sem_itens = threading.Semaphore(0)
        self.lock = threading.Lock()
        self.produtores = [threading.Thread(target=self.produzir, args=(i,)) for i in range(num_produtores)]
        self.consumidores = [threading.Thread(target=self.consumir, args=(i,)) for i in range(num_consumidores)]
        self.buffer_hist = []  # Histórico do tamanho do buffer
        self.producao_total = 0
        self.consumo_total = 0
        self.tempo_espera_produtores = []
        self.tempo_espera_consumidores = []

    def produzir(self, id_produtor):
        for _ in range(self.timesteps):
            start_wait = time.time()
            self.sem_espacos.acquire()  # Espera por espaço no buffer
            end_wait = time.time()
            self.tempo_espera_produtores.append(end_wait - start_wait)
            with self.lock:
                self.buffer.put(1)
                self.producao_total += 1
                self.buffer_hist.append(self.buffer.qsize())
                print(f"Produtor {id_produtor} produziu. Buffer atual: {self.buffer.qsize()}")
            self.sem_itens.release()
            time.sleep(0.1)  # Simula o tempo de produção

    def consumir(self, id_consumidor):
        for _ in range(self.timesteps):
            start_wait = time.time()
            self.sem_itens.acquire()  # Espera por itens disponíveis
            end_wait = time.time()
            self.tempo_espera_consumidores.append(end_wait - start_wait)
            with self.lock:
                self.buffer.get()
                self.consumo_total += 1
                self.buffer_hist.append(self.buffer.qsize())
                print(f"Consumidor {id_consumidor} consumiu. Buffer atual: {self.buffer.qsize()}")
            self.sem_espacos.release()
            time.sleep(0.1)  # Simula o tempo de consumo

    def iniciar(self):
        for produtor in self.produtores:
            produtor.start()
        for consumidor in self.consumidores:
            consumidor.start()
        for produtor in self.produtores:
            produtor.join()
        for consumidor in self.consumidores:
            consumidor.join()
        print("Simulação concluída!")

    def gerar_relatorio(self):
        print(f"Total produzido: {self.producao_total}")
        print(f"Total consumido: {self.consumo_total}")
        print(f"Tempo médio de espera dos produtores: {sum(self.tempo_espera_produtores)/len(self.tempo_espera_produtores):.2f}s")
        print(f"Tempo médio de espera dos consumidores: {sum(self.tempo_espera_consumidores)/len(self.tempo_espera_consumidores):.2f}s")

    def plotar_graficos(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.buffer_hist, label="Tamanho do Buffer ao Longo do Tempo", color="blue")
        plt.xlabel("Timesteps")
        plt.ylabel("Tamanho do Buffer")
        plt.title("Histórico do Tamanho do Buffer")
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == "__main__":
    # Parâmetros de entrada
    capacidade_buffer = 10
    num_produtores = 2
    num_consumidores = 3
    timesteps = 100

    linha = LinhaDeProducao(capacidade_buffer, num_produtores, num_consumidores, timesteps)
    linha.iniciar()
    linha.gerar_relatorio()
    linha.plotar_graficos()
