# coding: utf8
import xmlrpclib


@auth.requires_login()
def index():
     redirect(URL(request.application, 'tracksamples', 'data'))

@auth.requires_login()    
def data():
    count_recentkeys = 50 # number of recent keys to be fetched from Bionimbus database
    server=xmlrpclib.ServerProxy( 'https://bc.bionimbus.org/LIMS/keys/call/xmlrpc' )
    rows=server.recent_keys(count_recentkeys)
    
    #db.t_recentkeys.truncate('RESTART IDENTITY CASCADE')
    #insert/update count_recentkeys into db
    
    for row in rows:
        s=row
        bid = s[0].strip()
        logger.debug('bid:'+bid)
        db.t_recentkeys.update_or_insert(db.t_recentkeys.f_bid==bid,
            f_bid=bid,
            f_firstname=s[1].strip(),
            f_lastname=s[2].strip(),
            f_dategenerated=s[3],
            f_application=s[4].strip(),
            f_project=s[5].strip())
            
        
    query=db.t_recentkeys
    sortorder=[~db.t_recentkeys.f_dategenerated,db.t_recentkeys.id]
    form = SQLFORM.grid(query=query, create=False, deletable=False, editable=False, maxtextlength=64, paginate=25,orderby=sortorder)
    
    return dict(form=form,bid=s[0])
    
@auth.requires_login()    
def getstates():
    keys =  [ '2013-C1' ]  #  list of keys for which states are to be fetched from Bionimbus database
    server=xmlrpclib.ServerProxy( 'https://bc-dev.bionimbus.org/Bionimbus/states/call/xmlrpc' )
    
    #get a list of possible states, then a list of the hisory of states for the provided keys:
    rows=server.get_states( [ '2013-C1' ] )

    return dict(rows=rows)

    # update ( add to ) the states of these keys
    #row = server.set_states( [ ( '2013-C1' , 2 ) ] )rows=server.recent_keys(count_recentkeys)
