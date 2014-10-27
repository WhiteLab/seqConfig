# -*- coding: utf-8 -*-
import os
import datetime
import xlrd
import xlwt
import xmlrpclib
from datetime import date


import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from gluon.tools import Mail
from collections import defaultdict

def user(): return dict(form=auth())

def help():
    return dict()

def index():
    redirect(URL(request.application, 'default', 'config_spreadsheet'))

auth.settings.allow_basic_login = True

###############################################################################################################################################################################
""" To upload seq config spreadsheet on seqConfig home page for a new run
    calls checkformat on uploaded spreadsheet to validate before inserting it into table t_seq_config_spreadsheets

"""
###############################################################################################################################################################################

@auth.requires_login()
def config_spreadsheet():

    template = db().select(db.t_seq_config_template.ALL)
    form = SQLFORM( db.t_seq_config_spreadsheets)

    query = db.t_seq_config

    links = [lambda row: A('Show Lanes',_href=URL("default","showLanes",args=[row.id],user_signature=True)),
      lambda row: A('Create Readme',_href=URL("default","writeReadme",args=[row.id],user_signature=True)),
      lambda row: A('Upload Spsheet',_href=URL("default","uploadsheet",args=[row.id],user_signature=True)),
      lambda row: A('Delete Run',_href=URL("default","delRun",args=[row.id]))]

    sortorder=[~db.t_seq_config.created_on]
    form2 = SQLFORM.grid(query,links=links,create=False, details=False,deletable=False, editable=True , maxtextlength=64, paginate=10,orderby = sortorder)

   
    if form.process(onvalidation=checkformat).accepted:
        response.flash = "Sequence Config Spreadsheet Uploaded"

        run_name = form.vars.f_run_name
        id = form.vars.id
        process_config_spreadsheet_info(run_name,id)

        redirect(URL(request.application, 'default', 'config_spreadsheet'))

    elif (form.errors.val==-1):
        response.flash = "Could not find 'Run Details' page. Please download template and fill in your run details"+form.errors.ex
        form.errors.val=0
    elif (form.errors.val==-2):
        response.flash = "Could not find 'Lane' pages. Please download template and fill in your Lane details"+form.errors.ex
        form.errors.val=0
    elif form.errors:
        response.flash =  "Could not open with excel. Please upload files with extension .xls or .xlsx"+str(form.errors) #+str(xlrd.__VERSION__)

    return dict(template=template,  form=form, form2=form2)

###############################################################################################################################################################################
""" To upload seq config spreadsheet on seqConfig home page for an existing run with button 'Upload spheet'
    calls checkformat on uploaded spreadsheet to validate before inserting it into table t_seq_config_spreadsheets

"""
###############################################################################################################################################################################

def uploadsheet():
  
    seqid=request.args(0)
    session.seqid=seqid
  
    logger.debug('in upload sheet seqid'+str(seqid))
  
    #insert new file to db
    #get spsheet id
  
    row_s=db.t_seq_config(db.t_seq_config.id==seqid)
  
    logger.debug('row_s'+ str(row_s))
  
    spshid = int(row_s.f_spsheet_id)
    run_name = str(row_s.f_run_name)
  
    record=db.t_seq_config_spreadsheets[spshid]
    formUpload=SQLFORM(db.t_seq_config_spreadsheets, record)
  
  
    if formUpload.process(onvalidation=checkformat).accepted:
        
        response.flash = "Sequence Config Spreadsheet Uploaded for run " + run_name

        row    = db.t_seq_config_spreadsheets(db.t_seq_config_spreadsheets.id==spshid )
        fn      = row.f_file
        update_spreadsheet("applications/seqConfig/uploads/" + fn, run_name,spshid )
         
        # redirect to same page to refresh and show new rows in form2
        redirect(URL(request.application, 'default', 'config_spreadsheet'))

    elif (formUpload.errors.val==-1):
        response.flash = "Could not find 'Run Details' page. Please download template and fill in your run details"+form.errors.ex
        form.errors.val=0
    elif (formUpload.errors.val==-2):
        response.flash = "Could not find 'Lane' pages. Please download template and fill in your Lane details"+form.errors.ex
        form.errors.val=0
    elif formUpload.errors:
        response.flash =  "Could not open with excel. Please upload files with extension .xls or .xlsx"+str(form.errors) #+str(xlrd.__VERSION__)
 
    return dict(form=formUpload)

###############################################################################################################################################################################
""" To validate spreadsheet uploaded on seqConfig home page for a run

"""
###############################################################################################################################################################################
  
def checkformat(form):
  
    fn=request.vars.f_file.filename
    fc=request.vars.f_file.file.read()
 

    try:
    
        book = xlrd.open_workbook(file_contents=fc)
     
        #check for run details page
        sheetRun = book.sheet_by_name("Run Details")

        #check for at least a Lane page
        nolanes=0
        #sheet 0 - Run Details
        for ns in range(1,9): # check for Lanes numbered 1 to 8

            n="Lane"+ str(ns)
            try:
                sh= book.sheet_by_name(n)
            except:
                nolanes = nolanes +1
                pass

        if (nolanes == 8):
            form.errors.val=-2

    except Exception, ex:
        form.errors.ex =str(ex)
        form.errors.val=-1
     
  
    finally:
        #to move file pointer to beginning of file
        request.vars.f_file.file.seek(0,0)
        book.release_resources() 

###############################################################################################################################################################################
""" To delete a spreadsheet for a run 

"""
###############################################################################################################################################################################

def delRun():
    
    logger.debug('in delRun')
    logger.debug(str(request.args))
    
    record = db.t_seq_config(id=int(request.args[0]))

    sheetid= record.f_spsheet_id

    db(db.t_seq_config_spreadsheets.id==sheetid).delete()
    redirect(URL(request.application, 'default', 'config_spreadsheet'))

###############################################################################################################################################################################
""" To display Lane information as a grid 

"""
###############################################################################################################################################################################

@auth.requires_login()
def showLanes():
  
    logger.debug(str(request.args))

    # on first showlanes button click, save seqid in session variable, may be there is better condition to check
    if (len(request.args) == 1): 
        session.seqid = request.args(0)
      
  
    if (request.args(0) == 'new'):
        db.t_config_lane.f_seq_config_id.default=session.seqid # session variable has seqid
  
    seqid = session.seqid
  
    query =  (db.t_config_lane.f_seq_config_id==seqid)
    sortorder=[db.t_config_lane.f_lane_number, db.t_config_lane.f_sample_number ]
    form2 = SQLFORM.grid(query,create=True, details=False, deletable=True, editable=True, maxtextlength=64, paginate=25,orderby=sortorder)

  
    return dict(form2=form2)


###############################################################################################################################################################################
""" To validate entries in readme file

"""
###############################################################################################################################################################################

def validateReadme(seqid):


    if (uniqbarcode(seqid)==False):
        return False

    if (uniqbid(seqid)==False):
        return False

    if (uniqsn(seqid)==False):
        return False

    if (bbid(seqid)==False):
        return False
      
    if (bidexists(seqid)==False):
        return False
      
    #check for values in database, IS_IN_DB is at form level only
    #barcode exists
    if (bcexists(seqid)==False):
        return False
      
    # if barcode is none, its lane should have only one sample    
    if (checkbcnone(seqid)==False):
        return False    
   

    return True

###############################################################################################################################################################################
""" value none for a barcode is allowed only in non-multiplexed lanes

"""
###############################################################################################################################################################################

def checkbcnone(seqid):
  
    for n in range(1,9):

        # barcodes
        b=[]

        for row in db((db.t_config_lane.f_seq_config_id==seqid) & (db.t_config_lane.f_lane_number == n )).select():
            b.append(str(row.f_barcode).strip())
          
        # check for 'none'
        if (('none' in b) & (len(b) > 1)) :
            #error
            logger.debug('barcode-none in lane '+ str(n) + ', number of barcodes in this lane ' + str(len(b))) 
            session.flash=T('Barcode is none in a multiplexed lane ' +str(n)+ '.  Value \"none\" is allowed only if a single sample exists in a lane. ')
            return False
    return True

###############################################################################################################################################################################
""" Barcodes in readme are checked against database records 

"""
###############################################################################################################################################################################

def bcexists(seqid):

    #barcodes from database
    bc=[]
    rows =db(db.t_barcodes).select()
    for r in rows:
        bc.append(str(r.f_barcode))
  
    #list of barcodes that do not exist in database
  
    bne = {}
    logger.debug('len of bne, beginning ' + str(len(bne)))
  
    #check barcodes for all lanes
    for n in range(1,9):

        # barcodes
        b=[]

        for row in db((db.t_config_lane.f_seq_config_id==seqid) & (db.t_config_lane.f_lane_number == n )).select():
            b.append(str(row.f_barcode).strip())

      
        bne[n]=list(set(b).difference(set(bc)))
      
      
    logger.debug('barcodes not in db' + str(bne))
  
    msg = ''   
    logger.debug('len of bne, here' + str(len(bne))) 
    retFlag = True
    for x in bne.keys():
        if (len(bne[x]) > 0):
            retFlag = False
            s=' '.join(bne[x])
            msg = msg +  'Barcodes ' +s+ ' in lane '+ str(x) + ', '
         
    if (retFlag==False):
        session.flash=T(msg + ' are not found in database.  Please use Edit button to change values.')
  
  
    return retFlag
  
###############################################################################################################################################################################
""" BIDs in readme are checked against Bionimbus database records 

"""
###############################################################################################################################################################################
             
def bidexists(seqid):
  
    for n in range(1,9):
        bid=[]

        for row in db((db.t_config_lane.f_seq_config_id==seqid) & (db.t_config_lane.f_lane_number == n )).select():
              bid.append(str(row.f_bid))

        server=xmlrpclib.ServerProxy( 'https://bc.bionimbus.org/LIMS/keys/call/xmlrpc' )
        #server=xmlrpclib.ServerProxy( 'https://bc.bionimbus.org/Bionimbus/keys/call/xmlrpc' )
        for b in bid:
            de = server.does_key_exist( b )
           # logger.debug('debug de:'+str(de))
            if (de == True):
                pass
            else:
                session.flash=T('Bionimbus ID ' +b+ ' does not exist in Bionimbus database. Please visit www.bionimbus.org to create.')
                return False

    return True
###############################################################################################################################################################################
""" Barcodes should be unique in each lane

"""
###############################################################################################################################################################################
    

def uniqbarcode(seqid):

    dupb=defaultdict(list)

    for n in range(1,9):

        #unique barcode in every Lane
        b=[]

        for row in db((db.t_config_lane.f_seq_config_id==seqid) & (db.t_config_lane.f_lane_number == n )).select():
            b.append(str(row.f_barcode))


    
        dup=[]
        list1 = set()
        list1 = [dup.append(x) if x in list1 else list1.add(x) for x in b]


        if (len(dup) > 0):
           dupb[n]=[ x for x in dup]
    
    msg = ''         
    retFlag = True
    for x,v in dupb.items():
        
        if (len(v) > 0):
            retFlag = False
            s=' '.join(v)
            msg = msg +  'Barcodes ' +s+ 'are repeated in lane '+ str(x) + ', '
         
    if (retFlag==False):
        session.flash=T(msg + ' Barcodes should be unique for each lane.  Please use Edit button to change values.')
  
  
    return retFlag   

#    if (len(dupb)>0):
 #       for x in dupb:
  #          s=' '.join(dupb[x])
   #         session.flash=T('Barcodes ' +s+ ' are repeated in lane ' + str(x)+'. Barcode should be unique for each lane')

    #    return False

    #return True
###############################################################################################################################################################################
""" Bionimbus IDs should be unique in each lane

"""
###############################################################################################################################################################################
  
def uniqbid(seqid):

    dupbid=defaultdict(list)


    for n in range(1,9):
        bid=[]

        for row in db((db.t_config_lane.f_seq_config_id==seqid) & (db.t_config_lane.f_lane_number == n )).select():
            bid.append(str(row.f_bid))
        #unique BID in every Lane

        dup=[]
        list1 = set()
        list1 = [dup.append(x) if x in list1 else list1.add(x) for x in bid]


        if (len(dup) > 0):
            dupbid[n]=[ x for x in dup]


    msg = ''         
    retFlag = True
    for x,v in dupbid.items():
        if (len(v) > 0):
            retFlag = False
            s=' '.join(v)
            msg = msg +  'Bioimbus IDs ' +s+ 'are repeated in lane '+ str(x) + ', '
         
    if (retFlag==False):
        session.flash=T(msg + ' Bionimbus IDs should be unique for each lane.  Please use Edit button to change values.')
  
  
    return retFlag   

#      print len(dupbid)
 #     if (len(dupbid)>0):
  #       for x in dupbid:
   #          s=' '.join(dupbid[x])
    #         session.flash=T('Bionimbus IDs ' +s+ ' are repeated in lane ' + str(x)+'. Bionimbus ID should be unique for each lane')

     #    return False

      #return True
###############################################################################################################################################################################
""" Sample Numbers should be unique in each lane

"""
###############################################################################################################################################################################
  
def uniqsn(seqid):

    dupsn=defaultdict(list)


    for n in range(1,9):
        sn=[]

        for row in db((db.t_config_lane.f_seq_config_id==seqid) & (db.t_config_lane.f_lane_number == n )).select():
            sn.append(str(row.f_sample_number))


        dup=[]
        list1 = set()
        list1 = [dup.append(x) if x in list1 else list1.add(x) for x in sn]


        if (len(dup) > 0):
            dupsn[n]=[ x for x in dup]

    msg = ''         
    retFlag = True
    for x,v in dupsn.items():
        if (len(v) > 0):
            retFlag = False
            s=' '.join(v)
            msg = msg +  'Sample numbers ' +s+ 'are repeated in lane '+ str(x) + ', '
         
    if (retFlag==False):
        session.flash=T(msg + ' Sample numbers should be unique for each lane.  Please use Edit button to change values.')
  
  
    return retFlag   
#      print len(dupsn)
 #     if (len(dupsn)>0):
  #       for x in dupsn:
   #          s=' '.join(dupsn[x])
    #         session.flash=T('Sample numbers ' +s+ ' are repeated in lane ' + str(x)+'. Sample numbers should be unique for each lane')

     #    return False

      #return True


###############################################################################################################################################################################
""" Barcodes-BID pair should be unique across lanes

"""
###############################################################################################################################################################################
  
#consistent barcode-BID pair across lanes
def bbid(seqid):

    #dict of bid and barcode for all samples
    bb={}

    for row in db(db.t_config_lane.f_seq_config_id==seqid).select():
        bid1=str(row.f_bid)
        b1=str(row.f_barcode)

        #if bid1 exists as a key, check its value else insert (bid1,b1)

        if bid1 in bb:
            tmp=bb[bid1]
            if (tmp != b1):
                # this barcode is not equal to existing barcode for this bid key
                session.flash=T('Bionimbus ID ' +bid1+ ' is associated with barcodes ' + str(tmp)+' and ' + str(b1)+'. Bionimbus ID and Barcode pair should be consistent across lanes')
                return False

        else:
            bb[bid1] = b1

    return True

###############################################################################################################################################################################
""" On clicking button 'Create Readme', this function writes Readme file to location /home/www-data/web2py/applications/seqConfig/readmefiles/ on lims server

"""
###############################################################################################################################################################################
  

@auth.requires_login()
def writeReadme():
  
    logger.debug('in write readme')
 
    seqid=request.args(0)
    session.seqid=seqid
    readme=''
    retvalue = validateReadme(seqid)
    #previous run num
    prunnum=0
    logger.debug('validated Readme'+str(retvalue)+str(seqid))
  
    if( retvalue == True):
        #save previous run number for this seqid
      
        rows_readme= db(db.t_readme.f_seq_config_id==seqid).select()
        logger.debug('len rows_readme' + str(len(rows_readme)))
        
        if(len(rows_readme)>0):
        
            row_t1 = db.t_readme(db.t_readme.f_seq_config_id==seqid)
            prunnum=int(row_t1.f_file_num)
            logger.debug('using previous readmefile num'+str(prunnum))

      
        row_seqid = db.t_seq_config(db.t_seq_config.id==seqid)
      
        if (prunnum==0):
            num=db(db.t_readme).select(db.t_readme.f_file_num.max()).first()[db.t_readme.f_file_num.max()] 
    
            num=num+1
        else:
            num = prunnum #use previous readmefile num
          
        logger.debug('file number'+str(num))
        # This will create a new file or **overwrite an existing file**.
      
        filename='RunName'+str(row_seqid.f_run_name)+'Num'+str(num)+'.txt'
        fname='applications/seqConfig/readmefiles/'+filename
        f = open(fname, "w")
        
        string1 = makeRunstring(row_seqid,num)
        string2 = makeLanestring(seqid)
        readme = string1+string2

        f.write(readme)
        logger.debug('wrote Readme to readmefiles dir')
      
        f.close()
      
        #make excel file
      
        filename1='RunName'+str(row_seqid.f_run_name)+'Num'+str(num)+'.xls'
        fname1='applications/seqConfig/readmefiles/'+filename1
        makeReadmeExcel(fname1,row_seqid,num)
      

        #store files to database
        stream = open(fname,'rb')
        stream1 = open(fname1,'rb')
  
        #store file to database
        db.t_readme.update_or_insert(db.t_readme.f_file_num==num,f_seq_config_id=int(seqid),
          f_run_name=str(row_seqid.f_run_name),
          f_name=filename,
          f_file=db.t_readme.f_file.store(stream,filename),
          f_excel_file=db.t_readme.f_excel_file.store(stream1,filename1),
          f_file_num=num,
          f_status='Waiting for Approval')
      
        logger.debug('inserted readme files to database')
      
        msg = MIMEMultipart()
        content =' Run Name: '+str(row_seqid.f_run_name)+'\n'+'Run number: '+str(num)+'\n' +' Readme file status: Waiting for Approval'
        me='hgaclims@gmail.com' 
        mt=['pmakella@uchicago.edu','jhtuteja@uchicago.edu', 'jgrundstad@uchicago.edu','adamcdidier@gmail.com','murphymarkw@uchicago.edu',
            'cedwards.uc@gmail.com', 'gkuffel22@gmail.com']
        #mt =['pmakella@uchicago.edu']
      
        msg[ 'Subject' ] =  'Run Name: '+str(row_seqid.f_run_name) + '   --   created'
        msg[ 'From'    ] = me
        msg[ 'To'      ] = ",".join( mt )
      
        msg.attach( MIMEText(content) )
      
        #attach file
      
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(fname,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(fname))
        msg.attach(part)
      
        server = smtplib.SMTP( '127.0.0.1' )
        server.sendmail( me , mt , msg.as_string() )
        server.close()

        logger.debug('sent readme mail')

 
    else:
        # log error message and redirect
     
        logger.debug('errors in Readme')
        redirect(URL(request.application, 'default', 'showLanes'))


    return dict(readme=readme)

###############################################################################################################################################################################
""" Make excel version of Readme file 

"""
###############################################################################################################################################################################
   
def makeReadmeExcel(fn,row_seqid,num):

 
    seqid=row_seqid.id
    book = xlwt.Workbook(encoding="utf-8")
  
    #add runDetails sheet 
    sheetR = book.add_sheet("Run Details")
  
    #write run Details  
    sheetR.write(0, 0, "Run Name:" + str(num) )
    sheetR.write(1, 0, "Flow Cell ID: " + str(row_seqid.f_flow_cell_id) )
    sheetR.write(2, 0,    "Run Date: " + str(row_seqid.f_run_date))
    sheetR.write(3, 0,    "Read Type: " + str(row_seqid.f_read_type))
    sheetR.write(4, 0,    "Read 1 Cycles =  " +str (row_seqid.f_read_1_cycles))
    sheetR.write(5, 0,    "Read 2 Cycles =	" +str(row_seqid.f_read_2_cycles))
    sheetR.write(6, 0,    "Index Read Cycles = "+ str(row_seqid.f_index_read_cycles))
    sheetR.write(7, 0,    "Solexa = " + str(row_seqid.f_illumina))
    sheetR.write(8, 0,    "SNR = "+str(row_seqid.f_illumina_snr))
    sheetR.write(9, 0,    "Note: "+str(row_seqid.f_note))
  
    #write lane details
  
    for ln in range(1,9): 
       
        sh= book.add_sheet("Lane "+ str(ln))
        #write column heading
        sh.write(0,0,"Sample Number")
        sh.write(0,1,"Sample Name")
        sh.write(0,2,"Bionimbus ID")
        sh.write(0,3,"Requestor")
        sh.write(0,4,"Mapping Reference")
        sh.write(0,5, "Cluster Station Concentration")
        sh.write(0,6,"Barcode")
        sh.write(0,7,"QC or Production")
        rownum=1
        for row in db((db.t_config_lane.f_seq_config_id==seqid)& (db.t_config_lane.f_lane_number==ln)).select():
            sh.write(rownum,0,str(row.f_sample_number))
            sh.write(rownum,1,str(row.f_sample_name) )
            sh.write(rownum,2,str(row.f_bid))
            sh.write(rownum,3,str(row.f_requestor))
            sh.write(rownum,4,str( row.f_mapping_ref))          
            sh.write(rownum,5,str(row.f_cluster_station_conc))
            sh.write(rownum,6,str(row.f_barcode))
            sh.write(rownum,7, str(row.f_qc_prod))
            rownum=rownum+1
        
    book.save(fn)
 
###############################################################################################################################################################################
""" Show Readme files as a grid

"""
###############################################################################################################################################################################
 
def manageReadme():
    query =  db.t_readme
    sortorder=[db.t_readme.f_file_num]
  
    db.t_readme.created_on.readable = db.t_readme.created_by.readable = db.t_readme.modified_on.readable = db.t_readme.modified_by.readable = True
  
    fields = (db.t_readme.id,db.t_readme.f_seq_config_id, db.t_readme.f_run_name, db.t_readme.f_name, db.t_readme.f_file,db.t_readme.f_excel_file,db.t_readme.f_file_num,
             db.t_readme.created_on, db.t_readme.created_by, db.t_readme.modified_on, db.t_readme.modified_by)

    form = SQLFORM.grid(query,create=False,fields=fields, onupdate = writeFile,details=False,deletable=True, editable=is_user_admin(db,auth), maxtextlength=64, paginate=25,orderby=sortorder)

    return dict(form=form)

###############################################################################################################################################################################
""" On changing status to 'Approved' for a Readme file, this function writes Readme file to location 
    /home/www-data/web2py/applications/seqConfig/sequence_config_dir/ on lims server

"""
###############################################################################################################################################################################
   
def writeFile(form):
  
      logger.debug('in writeFile')
      seqid=form.vars.f_seq_config_id
  
      try:

          row_seqid = db.t_seq_config(db.t_seq_config.id==seqid)
        
          row_t= db.t_readme(db.t_readme.f_seq_config_id==seqid)

          n=int(row_t.f_file_num)
       
          num="{0:04d}".format(n)
          logger.debug('file number'+str(num))
          # This will create a new file or **overwrite an existing file**.
          filename=str(num)+'.txt'
          fname='applications/seqConfig/sequence_config_dir/'+filename
          f = open(fname, "w")
        
          string1 = makeRunstring(row_seqid,num)
          string2 = makeLanestring(seqid)
          readme = string1+string2

          f.write(readme)
          logger.debug('wrote Readme to seq config dir')
      finally:
          f.close()
      
   
      msg = MIMEMultipart()
      content =' Run Name: '+str(row_seqid.f_run_name)+'\n'+'Run number: '+str(num)+'\n' +' Readme file status changed to '+ str(row_t.f_status) 
      me='hgaclims@gmail.com' 
      mt=['pmakella@uchicago.edu','jhtuteja@uchicago.edu', 'jgrundstad@uchicago.edu','adamcdidier@gmail.com','murphymarkw@uchicago.edu']
      # mt = [ 'pmakella@uchicago.edu']
      
      msg[ 'Subject' ] = 'Run Name:  '+str(row_seqid.f_run_name) +'  --  '+ str(row_t.f_status) 
      msg[ 'From'    ] = me
      msg[ 'To'      ] = ",".join( mt )
      
      msg.attach( MIMEText(content) )
      
      #attach file
      
      part = MIMEBase('application', "octet-stream")
      part.set_payload( open(fname,"rb").read() )
      Encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(fname))
      msg.attach(part)
      
      server = smtplib.SMTP( '127.0.0.1' )
      server.sendmail( me , mt , msg.as_string() )
      server.close()

      logger.debug('sent readme mail')

###############################################################################################################################################################################
""" check if user is an admin

"""
###############################################################################################################################################################################
  
def is_user_admin( db , auth ):

  rows = db(
          ( db.auth_user.id == auth.user_id) &
          ( db.auth_user.is_admin == True )).select()

  return len( rows ) > 0

###############################################################################################################################################################################
""" make a string from Run Details for Readme file

"""
###############################################################################################################################################################################
 
def makeRunstring(row_seqid,num):
   
    mul=''
    # if a lane has samples>1, multiplex = true
    if(checkMultiplex(row_seqid)==True):
        mul='multiplex'
   
   
    string = ('Run Name: ' + str(num) + '\n' +
      'Flow Cell ID: ' + str(row_seqid.f_flow_cell_id) + '\n' +
      'Run Date: ' + str(row_seqid.f_run_date)	+ '\n' +
      'Read Type: ' + str(row_seqid.f_read_type)	+ ' '+ mul + '\n' +
      'Read 1 Cycles =  ' +str (row_seqid.f_read_1_cycles) + '\n' +
      'Read 2 Cycles =	' +str(row_seqid.f_read_2_cycles)+ '\n' +
      'Index Read Cycles = '+ str(row_seqid.f_index_read_cycles)+ '\n' +
      'Solexa = ' + str(row_seqid.f_illumina)	+ '\n' +
      'SNR = '+str(row_seqid.f_illumina_snr)+ '\n' +
      'Note: '+str(row_seqid.f_note) + '\n' )
    return string

###############################################################################################################################################################################
""" check if lanes is multiplexed

"""
###############################################################################################################################################################################
 
def checkMultiplex(row_seqid):
    #check if any of the 8 lanes have more than 1 sample
    seqid=str(row_seqid.id)
    
    for n in range(1,8):
         rows= db((db.t_config_lane.f_seq_config_id==seqid) & (db.t_config_lane.f_lane_number == n )).select()
         if (len(rows) >1):
              return True
              
    return False
    
###############################################################################################################################################################################
""" make a string from Lanes for Readme file

"""
###############################################################################################################################################################################
     
def makeLanestring(seqid):

    string = ('Lane;\tSample Name;\tDatabase Key;\tRequestor Name;\tMapping Reference File;\tCluster Station Concentration;\tIndex/Barcode;\tQCorProduction')
   
    for row in db(db.t_config_lane.f_seq_config_id==seqid).select(orderby=db.t_config_lane.f_lane_number|db.t_config_lane.f_sample_number):
        string = string + '\n'
        string = ( string + str(row.f_lane_number) + '-' + str(row.f_sample_number) + '\t' +
                 str( row.f_sample_name) + '\t' + str(row.f_bid) + '\t' + str(row.f_requestor) + '\t' +
                 str( row.f_mapping_ref)+ '\t' + (str(row.f_cluster_station_conc)).strip() + '\t' + (str(row.f_barcode)).strip() + '\t' + str(row.f_qc_prod))

    return string
###############################################################################################################################################################################
""" get latest file uploaded

"""
###############################################################################################################################################################################
 
def process_config_spreadsheet_info(run_name,id ):

    row =db(db.t_seq_config_spreadsheets.id>0).select(orderby=~db.t_seq_config_spreadsheets.created_on,limitby=(0,1)).first()

    fn      = row.f_file
  
    logger.debug('in process config sheet info : sheet id' + str(row.id))
    read_spreadsheet("applications/seqConfig/uploads/" + fn, run_name,id )

    return locals()

###############################################################################################################################################################################
""" check values read from spreadsheet

"""
###############################################################################################################################################################################
   
def checkdatamap(datamap):

    #raise exceptions, if any
  
   
    try:       
        num = datamap['Flow Cell ID']
    except (ValueError, KeyError), e :
        datamap['Flow Cell ID']='Could not read value from file'
 
  
    try:  
        read_type=datamap['Read Type']
        a=['paired','Paired']
        #read_type has 'paired', write paired-end
        if any(x in read_type for x in a):
            datamap['Read Type']='paired-end'
        
        b=['single', 'Single']
        if any(x in read_type for x in b):
            datamap['Read Type']='single-end'
    except (ValueError, KeyError), e :
        datamap['Read Type']='Could not read value from file'
  
    try:
        read_1_cycles=datamap['Read 1 Cycles']
    except (ValueError, KeyError), e :
        datamap['Read 1 Cycles']='Could not read value from file'
      
    try:    
        read_2_cycles=datamap['Read 2 Cycles']
    except (ValueError, KeyError), e :
        datamap['Read 2 Cycles']='Could not read value from file'
      
    try:    
        index_read_cycles=datamap['Index Read Cycles']
    except (ValueError, KeyError), e :
        datamap['Index Read Cycles']='Could not read value from file'
      
    try:    
        illumina=datamap['Illumina']
    except (ValueError, KeyError), e :
        datamap['Illumina']='Could not read value from file'
    try:    
        illumina_snr=datamap['Illumina SNR']
    except (ValueError, KeyError), e :
        datamap['Illumina SNR']='Could not read value from file'
    try:
        note=datamap['Note']
    except (ValueError, KeyError), e :
        datamap['Note']='None'

###############################################################################################################################################################################
""" read uploaded spreadsheet and insert records into tables t_seq_config, t_config_lane

"""
###############################################################################################################################################################################
        
def read_spreadsheet(fn,run_name,id):
    try:
        logger.debug('in read spreadsheet')
   
        book = xlrd.open_workbook( fn )

        sheetRun = book.sheet_by_name("Run Details")

        data=[]
        datamap={}
        for i in range(sheetRun.nrows):
            row = sheetRun.row_values(i)
            for r in row:
                data.append(str(r).strip())

        #make dict, add None if list has odd number of items for any reason
        datamap = dict( map ( None, *[iter(data)]*2))
        #add exceptions for KeyError and ValueError

        #check for ValueError exceptions and modify values causing exceptions
        checkdatamap(datamap)
   
        ##date
        try:
            date_as_number=int(float(datamap['Run Date']))
            year, month, day,hour, minute, second  = xlrd.xldate_as_tuple(date_as_number, book.datemode)
            py_date = datetime.date(year,month,day)
        except (ValueError, KeyError), e :
            py_date =  date.today()


        db.t_seq_config.insert(f_run_name=run_name,
         f_spsheet_id=int(id),
         #changed datatype from int to strin
         #f_flow_cell_id=int(float(datamap['Flow Cell ID'])),
         f_flow_cell_id=datamap['Flow Cell ID'],
         f_read_type=datamap['Read Type'],
         f_read_1_cycles=datamap['Read 1 Cycles'],
         f_read_2_cycles=datamap['Read 2 Cycles'],
         f_index_read_cycles=datamap['Index Read Cycles'],
         f_illumina=datamap['Illumina'],
         f_illumina_snr=datamap['Illumina SNR'],
         f_run_date=py_date,
         f_note=datamap['Note']
         )


        #read data for from lane sheets
        record = db.t_seq_config(f_spsheet_id=int(id))
  

        keys=['Sample Number','Sample Name', 'Bionimbus ID', 'Requestor', 'Mapping Reference', 'Cluster Station Concentration', 'Barcode','QC or Production']
        values=[]
        #default indices
        for i in range(len(keys)):
            values.append(i)

 
        #skip sheet 0 - Run Details
        for ns in range(1,book.nsheets):
            num=ns
            n="Lane"+ str(num)
            sh = book.sheet_by_name(n)
    

            for i in range(sh.nrows):
                row = sh.row_values(i)

                lndata=[]
                if i==0:
                    # row with column names, indices from sheet
                    for r in row:
                        lndata.append(str(r).strip())

                    #get indices for fields

                    for ind, item in enumerate(keys):
                        try:
                            values[ind]=lndata.index(item)
                        except ValueError:
                            values[ind]=1 # no match, arbitrary index to fill grid with some number

         

                elif i>0:
                    # rows with data
                    lndata=[]
                    for r in row:
                        lndata.append(str(r).strip())

        
                    db.t_config_lane.insert(f_seq_config_id = record.id, f_lane_number = ns, f_sample_number=int(float(lndata[values[0]])),
                     f_sample_name=lndata[values[1]],
                     f_bid=lndata[values[2]],
                     f_requestor=lndata[values[3]],
                     f_mapping_ref=lndata[values[4]],
                     f_cluster_station_conc=lndata[values[5]],
                     f_barcode=lndata[values[6]],
                     f_qc_prod=lndata[values[7]])
    finally:
        book.release_resources() 
###############################################################################################################################################################################
""" read uploaded spreadsheet and update (or insert) records in tables t_seq_config, t_config_lane

"""
###############################################################################################################################################################################
   
def update_spreadsheet(fn,run_name,id):

    try:
   
        seqid=session.seqid


        logger.debug('in update spread sheet')
        book = xlrd.open_workbook( fn )

        sheetRun = book.sheet_by_name("Run Details")

        data=[]
        datamap={}
        for i in range(sheetRun.nrows):
            row = sheetRun.row_values(i)
            for r in row:
                data.append(str(r))

        #make dict, add None if list has odd number of items for any reason
        datamap = dict( map ( None, *[iter(data)]*2))
        #add exceptions for KeyError and ValueError

        #check for ValueError exceptions and modify values causing exceptions
        checkdatamap(datamap)
   
        ##date
        try:
            date_as_number=int(float(datamap['Run Date']))
            year, month, day,hour, minute, second  = xlrd.xldate_as_tuple(date_as_number, book.datemode)
            py_date = datetime.date(year,month,day)
        except (ValueError, KeyError), e :
            py_date =  date.today()

        db.t_seq_config.update_or_insert(db.t_seq_config.id==seqid,f_run_name=run_name,
           f_spsheet_id=int(id),
           #changed datatype from int to string
           #f_flow_cell_id=int(float(datamap['Flow Cell ID'])),
           f_flow_cell_id=datamap['Flow Cell ID'],
           f_read_type=datamap['Read Type'],
           f_read_1_cycles=datamap['Read 1 Cycles'],
           f_read_2_cycles=datamap['Read 2 Cycles'],
           f_index_read_cycles=datamap['Index Read Cycles'],
           f_illumina=datamap['Illumina'],
           f_illumina_snr=datamap['Illumina SNR'],
           f_run_date=py_date,
           f_note=datamap['Note']
           )


        #read data for from lane sheets
        record = db.t_seq_config(f_spsheet_id=int(id))
   

        keys=['Sample Number','Sample Name', 'Bionimbus ID', 'Requestor', 'Mapping Reference', 'Cluster Station Concentration', 'Barcode','QC or Production']
        values=[]
        #default indices
        for i in range(len(keys)):
            values.append(i)

   
        #delete lane info for seqid
        query = (db.t_config_lane.f_seq_config_id == seqid)
        setrows = db(query)
        setrows.delete()

        #sheet 0 - Run Details
        for ns in range(1,book.nsheets):
            num=ns
            n="Lane"+ str(num)
            sh = book.sheet_by_name(n)

            for i in range(sh.nrows):
                row = sh.row_values(i)

                lndata=[]
                if i==0:
                    # row with column names, indices from sheet
                    for r in row:
                        lndata.append(str(r))

                    #get indices for fields

                    for ind, item in enumerate(keys):
                        try:
                            values[ind]=lndata.index(item)
                        except ValueError:
                            values[ind]=1 # no match, arbitrary index to fill grid with some number

         
                elif i>0:
                    # rows with data
                    lndata=[]
                    for r in row:
                        lndata.append(str(r))

                    db.t_config_lane.insert(f_seq_config_id=record.id, f_lane_number = ns, f_sample_number=int(float(lndata[values[0]])),
                     f_sample_name=lndata[values[1]],
                     f_bid=lndata[values[2]],
                     f_requestor=lndata[values[3]],
                     f_mapping_ref=lndata[values[4]],
                     f_cluster_station_conc=lndata[values[5]],
                     f_barcode=lndata[values[6]],
                     f_qc_prod=lndata[values[7]])
    finally:
        book.release_resources() 
###############################################################################################################################################################################
""" default download function

"""
###############################################################################################################################################################################
 
def download():
    return response.download(request, db,attachment=True)
###############################################################################################################################################################################
""" To download sequence config templates

"""
###############################################################################################################################################################################
 
def download_template():
    
	import cStringIO
	import contenttype as c
	 
	file_id = request.args(0)      
	s=cStringIO.StringIO()

	(filename,file) = db.t_seq_config_template.f_file.retrieve(db.t_seq_config_template[file_id].f_file)
	s.write(file.read())
	response.headers['Content-Type'] = c.contenttype(filename)
	response.headers['Content-Disposition'] = \
	                "attachment; filename=%s" % filename
	return s.getvalue()
