from http.server import HTTPServer, BaseHTTPRequestHandler

tracks = []
playlist = []
generatingPlaylist = 0

# Lida com as requisições
class dataHandler(BaseHTTPRequestHandler):
        
    def do_GET(self):

        global generatingPlaylist
        if(self.path.endswith('/tracks')):
            if(len(tracks) > 0):
                generatingPlaylist = 1
                self.send_response(200)
                self.send_header('content-type', 'application/json')
                self.end_headers() 
                self.wfile.write(tracks.pop(0))  
            else:
                self.send_response(400)
                self.end_headers()

        elif(self.path.endswith('/playlist')):
            
            # Playlist gerada 
            if(len(playlist) > 0):
                self.send_response(200)
                self.send_header('content-type', 'application/json')
                self.end_headers()  
                self.wfile.write(playlist.pop(0))
               
                if(len(playlist) == 0):
                    generatingPlaylist = 0
            else:
                print(generatingPlaylist)
                # Playlist sendo gerada 
                if(bool(generatingPlaylist)):
                    # Envia processing status
                    self.send_response(102)
                    self.end_headers()
                # Playlist não foi gerada, e não existem dados relativos a ela
                else:
                    # Envia bad request status
                    self.send_response(400)
                    self.end_headers()
        # Rota Inexistente
        else:
            self.send_error(404)

    def do_POST(self): 
        if(self.path.endswith('/tracks')):
            # Envio dos Dados
            length = int(self.headers['content-length'])
            post_data = self.rfile.read(length)
            tracks.append(post_data)

            self.send_response(201)
            self.send_header('content-type', 'application/json')
            self.end_headers()
        elif(self.path.endswith('/playlist')):
            # Retorno da Playlist
            length = int(self.headers['content-length'])
            post_data = self.rfile.read(length)
            playlist.append(post_data)

            self.send_response(201)
            self.send_header('content-type', 'application/json')
            self.end_headers()
        # Rota Inexistente
        else:
            self.send_error(404)
            self.send_header('content-type', 'raw')
            self.wfile.write('Rota inexistente')



# Main
try:

    PORT = 3001
    server = HTTPServer(('', PORT), dataHandler)
    print('Server running on port %s' % PORT)
    server.serve_forever()

except KeyboardInterrupt:
    print('\n^C received. Shutting down the server')
    server.socket.close()