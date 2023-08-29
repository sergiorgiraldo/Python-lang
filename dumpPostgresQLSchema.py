import psycopg2

# ORIGIN ***************************************************************************

connOrigin = psycopg2.connect(database="mine", user="GK47LX", host="localhost", port="5432")
curOrigin = connOrigin.cursor()

with open("blahOrigin.csv", "w") as f:
    curOrigin.copy_expert(f"COPY ALPHA.BLAH TO STDOUT WITH HEADER CSV", f)

with open("rolesOrigin.csv", "w") as f:
    curOrigin.copy_expert(f"COPY ALPHA.ROLES TO STDOUT WITH HEADER CSV", f)

curOrigin.close()
connOrigin.close()

# DESTINATION **********************************************************************

connDest = psycopg2.connect(database="mine", user="GK47LX", host="localhost", port="5432")
curDest = connDest.cursor()

curDest.execute("delete from DELTA.BLAH")
with open("blahOrigin.csv", "r") as f:
    curDest.copy_expert(f"COPY DELTA.BLAH FROM STDIN WITH HEADER CSV", f)

curDest.execute("delete from DELTA.ROLES")
with open("rolesOrigin.csv", "r") as f:
    curDest.copy_expert(f"COPY DELTA.ROLES FROM STDIN WITH HEADER CSV", f)

connDest.commit()
curDest.close()
connDest.close()