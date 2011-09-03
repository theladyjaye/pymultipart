HTTP Multipart Body Parser
===========================

Pretty fast little parser for Multipart Form Bodies.
In the sample, full message body is 90,029 bytes and it takes 
the parser, on average, about 2.7ms to process it all 
and return the data.

It does **not** take into account **Content-Disposition: multipart/mixed**