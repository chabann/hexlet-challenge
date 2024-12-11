import re
import multiprocessing as mp
from time import sleep


class ServersQueue:
    def __init__(self):
        print("Добро пожаловать в симулятор распределенной системы.")
        self.servers_count = 0
        self.queue: list = []
        self.state = []
        self.summary_load = []

    def init_servers(self):
        print("Введите количество серверов:")
        self.servers_count = int(input())
        self.state = mp.Array('i', [0 for _ in range(self.servers_count)])

        manager = mp.Manager()
        self.queue = manager.list()

        for _ in range(self.servers_count):
            self.summary_load.append(0)

        self.write_servers_state(output_queue=False)

    def write_servers_state(self, output_queue: bool = True):
        for i in range(self.servers_count):
            work_text = f"выполняет задание (осталось {self.state[i]} сек.)"
            free_text = "пусто"
            print(f"Сервер {i + 1}: {work_text if self.state[i] else free_text}")

        if output_queue:
            print(f"Очередь заданий: {self.queue if len(self.queue) else 'нет'}")

    def new_task(self, seconds: int):
        servers_priority = sorted(
            [(i, self.summary_load[i], self.state[i]) for i in range(self.servers_count) if self.state[i] == 0],
            key=lambda x: x[1]
        )
        if servers_priority:
            server_id = servers_priority[0][0]
            self.summary_load[server_id] += seconds
            self.state[server_id] = seconds
            print(f"Задание с {seconds} секундами выполнения направлено на Сервер {server_id + 1}.")
            p = mp.Process(target=self.process_task, args=[self.state, self.queue, server_id])
            p.start()
        else:
            servers_priority = sorted([(i, self.summary_load[i]) for i in range(self.servers_count)], key=lambda x: x[1])
            server_id = servers_priority[0][0]
            self.queue.append(seconds)
            self.summary_load[server_id] += seconds
            print(f"Задание с {seconds} секундами выполнения добавлено в очередь. {self.queue}")

    def process_task(self, state: list, queue: list, server_id: int):
        while state[server_id] > 0:
            sleep(1)
            state[server_id] -= 1

        if not len(queue):
            print(f"Сервер {server_id + 1} завершает выполнение.")
        else:
            new_task_seconds = queue.pop(0)
            print(f"Сервер {server_id + 1} освобождается, задание из очереди направлено на Сервер {server_id + 1}.")
            state[server_id] = new_task_seconds
            self.process_task(state, queue, server_id)

    def wait_command(self):
        command = input()
        while command:
            if "Команда" in command:
                seconds = re.findall(r'\d+', command)
                self.new_task(int(seconds[-1]))
            elif "Состояние серверов" in command:
                self.write_servers_state()

            command = input()


if __name__ == '__main__':
    processes = ServersQueue()
    processes.init_servers()
    processes.wait_command()
