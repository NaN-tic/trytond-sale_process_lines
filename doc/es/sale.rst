#:after:sale/sale:paragraph:documents_lines#

Tenemos que tener en cuenta que cuando procesemos líneas individualmente, en el
momento de crear la factura o albarán se nos generarán por el número de
líneas procesadas a la vez. Es decir, si procesamos una sola línea, se nos
generará una factura y un albarán con la línea procesada. Si procesamos dos
líneas a la vez, se nos generará una factura y un albarán con dos líneas.

#:before:sale/sale:paragraph:process_lines#

Una vez hecho esto, se nos abrirá una ventana emergente donde podremos elegir
si procesamos toda la venta a la vez o si solo vamos a procesar alguna de las
líneas de la venta. En caso de que queramos procesar todas las líneas de la
venta clicaremos en el botón "Procesar venta" y tanto la venta como las líneas
que estaban pendientes de procesar cambiarán su estado a "En proceso". Si por
el contrario solo queremos procesar algunas líneas de la venta, las deberemos
seleccionar clicando en el símbolo "+" y, posteriormente, dándole a *Aceptar* y
a *Procesar Líneas*. Hay que tener en cuenta que solo es posible procesar
líneas individualmente si estas tienen un producto asociado en la venta, por lo
que si tenemos líneas sin producto las deberemos procesar junto con el resto
de la venta clicando en "Procesar venta".

Una vez procesadas las líneas, veremos que el color de estas cambia a verde
y el resto se mantienen en negro, de esta forma podremos localizar de una forma
visual las líneas procesada y diferenciarlas de las que todavía no lo están.

Por medio de |lines_menu| podremos acceder a un listado de las líneas de venta,
agrupadas por pestañas en líneas *a procesar*, *a procesar sin producto* y por
último un listado de todas las líneas independientemente de su estado. En esta
última pestaña también podremos diferenciar entre las líneas procesadas (en
verde) y las que no (en negro) por su color.

.. |lines_menu| tryref:: sale_process_line.menu_sale_line_form/complete_name