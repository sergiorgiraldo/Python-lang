from wsgiref.simple_server import make_server
import random
import string
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.session import SignedCookieSessionFactory
import geruWrapper
import geruDbEngine

def intro(request):
    return Response("Web Challenge 1.0")

def quotes(request):
    sessionIdentifier = "".join(random.choice(string.ascii_letters) for i in range(12))
    if not "sessionIdentifier" in request.session:
        request.session["sessionIdentifier"] = sessionIdentifier

    geruDbEngine.Insert(request.url, request.session["sessionIdentifier"])

    dict = geruWrapper.get_quotes()

    hasQuoteNumber = True

    if (request.url.endswith("random")):
        quoteNumber = random.randint(0, len(dict["quotes"]))
    else:    
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

def sessions(request):
    rows = geruDbEngine.GetSessions()
    response = "<ol>"
    for row in rows:
        response += "<li>" + row.identifier + "--" + row.page + "--" + str(row.dt) + "</li>"
    response += "</ol>"

    return Response(response)

if __name__ == "__main__":
    with Configurator() as config:
        config.add_route("intro", "/")
        config.add_view(intro, route_name="intro")
        
        config.add_route("quotes", "/quotes")
        config.add_view(quotes, route_name="quotes")
        
        config.add_route("quotesByNumber", "/quotes/{nb}")
        config.add_view(quotes, route_name="quotesByNumber")

        config.add_route("quotesRandom", "/quotes/random")
        config.add_view(quotes, route_name="quotesRandom")

        config.add_route("sessions", "/sessions")
        config.add_view(sessions, route_name="sessions")

        sessionFactory = SignedCookieSessionFactory("276t7BF7&SZNYnA92p$P")
        config.set_session_factory(sessionFactory)

        app = config.make_wsgi_app()
    server = make_server("0.0.0.0", 6543, app)
    server.serve_forever()