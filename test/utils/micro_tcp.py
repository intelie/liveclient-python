import multiprocessing as mp
import socket


class MicroTcpServer:
    def __init__(self, server_addr):
        self.output_queue = mp.Queue()
        self.process = mp.Process(target=self.run, args=[server_addr, self.output_queue])
        self.process.start()

    def run(self, server_addr, output_queue):
        # Create the socket and listen:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                serversocket.bind(server_addr)
                serversocket.listen(5)
                break
            except OSError:
                raise

        # Wait for a connection and message:
        (clientsocket, address) = serversocket.accept()
        buffer, sender = clientsocket.recvfrom(1024)
        message = buffer.decode("utf-8")
        output_queue.put(message)
        serversocket.shutdown(socket.SHUT_RDWR)
        serversocket.close()

    def close(self):
        if self.process.is_alive():
            while not self.output_queue.empty():
                self.output_queue.get(False)
            self.output_queue.close()
            self.output_queue.join_thread()
            self.process.terminate()
