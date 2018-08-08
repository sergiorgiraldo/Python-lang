from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
import geru.wrapper

def intro(request):
    return Response("Web Challenge 1.0")

def quotes(request):
    dict = geru.wrapper.get_quotes()

    hasQuoteNumber = True

    if 'nb' in request.matchdict:
        if not request.matchdict["nb"].isdigit():
            hasQuoteNumber = False
        else:
            quoteNumber = int(request.matchdict["nb"])
            if quoteNumber > len(dict["quotes"]):
                hasQuoteNumber = False
    else:
        hasQuoteNumber = False

    if hasQuoteNumber:
        response = "<h3>" + dict["quotes"][quoteNumber] + "</h3>"
    else:    
        response = "<ul>"
        for q in dict["quotes"]:
            response += "<li>" + q + "</li>"
        response += "</ul>"

    return Response(response)

if __name__ == "__main__":
    with Configurator() as config:
        config.add_route("intro", "/")
        config.add_view(intro, route_name="intro")
        
        config.add_route("quotes", "/quotes")
        config.add_view(quotes, route_name="quotes")
        
        config.add_route("quotesByNumber", "/quotes/{nb}")
        config.add_view(quotes, route_name="quotesByNumber")

        app = config.make_wsgi_app()
    server = make_server("0.0.0.0", 6543, app)
    server.serve_forever()