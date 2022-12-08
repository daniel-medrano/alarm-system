
# Requerimientos

### Armar y desarmar alarma.

 - El programa debe tener las funciones armar y desarmar alarma.
 - Estas funciones deben funciones con el push button.

 ### Indicador de alarma.

 - Utilizar un led debe indicar si la alarma esta armada o desarmada, 
 con verde y rojo respectivamente.
 
 ### Medición de distancia.

 - [x] Crear una función que mida la distancia en *cm* cuando es llamada.

 ### Telegram.
 
 - Si algo se encuentra dentro de los 30 cm, se enviará un mensaje 
 "Cuidado se ha detectado un objeto a: xx cm”.

 - Si algo **NO** se encuentra dentro de los 30, no se debe enviar 
 una alerta. Solamente mostrar en la terminal "Distancia asegurada" 
 cada 60 segundos.

 - Siempre se debe mostrar la medición en tiempo real con 
 "Distancia: XX cm".

 - La terminal debe mostrar ***"¡Alerta! ¡Alerta!"*** cuando algo 
 este en el rango de los 30 cm.

 - El bot de Telegram debe funcionar con los siguientes comandos.
    - /help
    - /distance
    - /alarmOn
    - /alarmOff
