import time
import threading
import msvcrt


class Palillo(object):      #Clase que represenata los palillos a utilizar por los filósofos en el cualse definen 2 funciones (además de la inicialización)... 
                            # y estas son la función tomar y la finción soltar

    def __init__(self, idPalillo):      #Inicialización de la clase palillos
        self.idPalillo = idPalillo      #Id del palillo para poder identificarlo 
        self.numFilosofo = -1            #Id del filosofo que esta haciendo uso del palillo (inicialmente tiene un valor de -1 al no ser usado por ningún filósofo)
        self.ocupado = False            #Variable booleana que nos indica si el palillo está en uso o no
        self.monitor = threading.Condition(threading.Lock())    #Monitor usado para la sincronización
        

    def tomar(self, idfilosofo):     # Función utilizada para que mediante la sincronización(monitores) se tome el palillo solicitado
        with self.monitor:                  #Ver Nota al final del codigo   
            while self.ocupado == True:       
                self.monitor.wait()         #Si el palillo esta siendo usado por otro filóloso entonces entra en un estado de bloqueo hasta que es despertado por notyfyAll 
            self.ocupado = True             #Cambio del estado del palillo a ocupado
            self.numFilosofo = idfilosofo   #Al palillo se le pasa el id del filósofo para saber quien lo utiliza
            print("El filósofo {0} tomó el palillo {1}".format(self.numFilosofo,self.idPalillo))
            self.monitor.notifyAll()        #Despierta todos los hilos que esperan en esta condición.

    def soltar(self, idfilosofo):         # Función utilizada para que mediante la sincronización(monitores) se suelte el palillo solicitado
        with self.monitor:                  #Ver Nota al final del codigo   
            while self.ocupado == False:
                self.monitor.wait()         #Si el palillo no esta siendo usado por un filóloso entonces entra en un estado de bloqueo hasta que es despertado por notyfyAll(esta comparacion podria ser eliminada pero se mantiene para evitar errores de bloqueo)
            self.ocupado = False            #Cambio del estado del palillo a liberado
            self.numFilosofo = -1           #El palillo vuelve a no estar asignado
            print("El filósofo {0} soltó el palillo {1}".format(idfilosofo,self.idPalillo))
            self.monitor.notifyAll()        #Despierta todos los hilos que esperan en esta condición.


class Filosofo (threading.Thread):      #Clase que hace representación  de los filósofos teniendo su función de inicialización y la función run que empieza todo...  
                                        # todo el proceso que cada filósofo debe de seguir. Cabe mencionar que esta clase es un hilo de ejecución

    def __init__(self, idfilosofo, izquierda, derecha,mesero,lleno):   #inicialización de la clase filósofo
        threading.Thread.__init__(self)
        self.idfilosofo = idfilosofo        #Id del filósofo para poder identificarlo 
        self.izquierda = izquierda          #A la variable izquierda se le va a asignar itra de tipo palillo, para asi poder tener las funciones de tomar y soltar para la mano izquierda                
        self.derecha = derecha              #A la variable derecha se le va a asignar itra de tipo palillo, para asi poder tener las funciones de tomar y soltar para la mano derecha
        self.mesero = mesero                #Mesero creado para evitar problemas de interbloqueo
        self.lleno = lleno                  #Variable a la que se le asigna el valor que representa hasta cuando el filósofo va a dejar de comer

    def run(self):                      #Función que sirve para ejecutar ya que esta clase es un Thread
        for i in range(self.lleno):
            self.mesero.sentarse()                  # El mesero permite al filósofo sentarse en la mesa
            print("El filósofo {0} está pensando".format(self.idfilosofo))
            time.sleep(0.2)                         # El filósofo pensará por 0.2 segundos
            self.izquierda.tomar(self.idfilosofo)   # El filósofo intentara tomar el palillo izquierdo
            self.derecha.tomar(self.idfilosofo)     # El filósofo intentara tomar el palillo derecho
            print("El filósofo {0} está comiendo".format(self.idfilosofo))
            time.sleep(0.2)                         # El filósofo empezará a comer por 0.2 segundos
            self.derecha.soltar(self.idfilosofo)    # El filósofo suelta el palillo izquierdo
            self.izquierda.soltar(self.idfilosofo)  # El filósofo suelta el palillo derecho
            self.mesero.levantarse()                # El mesero permite al filósofo levantarse de la mesa dejando un lugar disponible
        print("------------------------El filósofo {0} ya está lleno------------------------".format(self.idfilosofo))

class Mesero(object):           #Clase que servirá para evitar el deadlock, imaginando un monitor que sirve como un mesero permitiendole solo...
                                #sentarse a n-1 filósofos
    def __init__(self, disponible):
        self.monitor = threading.Condition(threading.Lock()) #Asignación del monitor
        self.disponible = disponible    #Numero de lugares disponibles

    def levantarse(self):             #Función de sincronización que deja un espacio libre para otro filósofo 
        with self.monitor:                  #Ver Nota al final del codigo   
            self.disponible += 1            #Aumenta la cantidad de lugares disponibles 
            self.monitor.notify()           #Despierta al hilo que espera en esta condición.

    def sentarse(self):                #Función de sincronización que le permite a un filósofo sentarse y comer 
        with self.monitor:                  #Ver Nota al final del codigo   
            while self.disponible == 0:
                self.monitor.wait()         #Mientras que la cantidad de lugares disponebles se 0 entoncces entonces se entra en un bloqueo de espera  
            self.disponible -= 1            #Caundo se sale de ese bloque y el filósofo puede sentarse entonces la disponibilidad disminuye

def main():

    n = 5               #Número de filósofos
    lleno = 3           #Cuantas veces debe de comer cada filósofo antes de llenarse y dejar de comer
    palillos = []       #Lista que va a contener todos los palillos
    filosofos = []      #Lista que va a contener a todos los filósofos

    print("\tProblema de la cena de los Filósofos con monitores")
    print("\t           Sistemas Operativos 1")
    print("\t                  Equipo 4")
    print("\t       Brenda Karen Miranda Hernández")
    print("\t      José Octavio Echevarría Sánchez\n")

    for i in range(n):
        palillos.append(Palillo(i))     #Se añaden todos los palillos a la lista "palillos"

    mesero = Mesero(n-1)        #Se crea un nuevo monitor que funciona como un mesero para poder así evitar el deadlock

    for i in range(n):
        filosofos.append( Filosofo(i, palillos[i], palillos[(i+1)%n], mesero, lleno))  #Se añaden todos los filósofos a la lista "filósofos" 

    for i in range(n):
        filosofos[i].start()        #Se inicia el proceso con cada uno de los filósofos


if __name__ == "__main__":
    main()


    '''Nota: se utilizó para las lineas de código señaladas una estructura ya establecida en python hablando de sincoronización de procesos
          que es la siguiente:

                        with self.monitor: 
                            # realiza algo...

        y de acuerdo a la documentación esto es igual a :

                        monitor.acquire()
                        try:
                            # realiza algo...
                        finally:
                            monitor.release()

        Por lo cual nos ahorra tiempo y cantidad de codigo con una simple linea'''