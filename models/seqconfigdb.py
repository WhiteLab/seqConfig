db.define_table( 't_seq_config' , ## seq_config ID record is created on each spreadsheet
    Field('f_spsheet_id', type='reference t_seq_config_spreadsheets',label=T('Sprsheet ID')),
    Field('f_run_name', type='string',label=T('Run Name')),
    Field('f_flow_cell_id', type='string',requires = IS_NOT_EMPTY(),label=T('Flow Cell ID')),
    Field('f_read_type', type='string',requires = IS_NOT_EMPTY(),label=T('Read Type')),
    Field('f_read_1_cycles', type='string',requires = IS_NOT_EMPTY(),label=T('Read 1 Cycles')),
    Field('f_read_2_cycles', type='string',requires = IS_NOT_EMPTY(),label=T('Read 2 Cycles')),
    Field('f_index_read_cycles', type='string',requires = IS_NOT_EMPTY(),label=T('Index Read Cycles')),
    Field('f_illumina', type='string',requires = IS_NOT_EMPTY(),label=T('Illumina')),
    Field('f_illumina_snr', type='string',requires = IS_NOT_EMPTY(),label=T('Illumina SNR')),
    Field('f_run_date', type='date',requires = IS_NOT_EMPTY(),label=T('Run Date')),
    Field('f_note', type='string',requires = IS_NOT_EMPTY(),label=T('Note')),
    auth.signature
    )

db.define_table( 't_config_lane' ,
    Field('f_seq_config_id', notnull=True,type='reference t_seq_config',label=T('Seq Config ID')), ## each seq_config ID should give 8 lanes x 48 samples records
    Field('f_lane_number', type='integer',requires = IS_NOT_EMPTY(),label=T('Lane Number')), ## to represent 8 lanes
    Field('f_sample_number', type='integer',requires = IS_NOT_EMPTY(), label=T('Sample Number')), ## to represent 48 samples in each lane
    Field('f_sample_name', type='string',label=T('Sample Name')),
    Field('f_bid', type='string',requires = IS_NOT_EMPTY(),label=T('Bionimbus ID')),
    Field('f_requestor', type='string',requires = IS_NOT_EMPTY(),label=T('Requestor')),
    Field('f_mapping_ref', type='string',label=T('Mapping Reference')),
    Field('f_cluster_station_conc', type='string',requires = IS_NOT_EMPTY(),label=T('Cluster Station Concentration')),
    Field('f_barcode', type='string',label=T('Barcode')),
    Field('f_qc_prod',type='list:string',label=T('QC or Production')),
    auth.signature
    )

db.define_table( 't_seq_config_spreadsheets',
    Field('f_run_name',type='string',requires = IS_NOT_EMPTY(),unique=True,label=T('Run Name')),
    Field('f_file','upload', requires = IS_NOT_EMPTY(),label=T('Spreadsheet To Upload')),
    auth.signature
    
    )

db.define_table( 't_seq_config_template',
    Field('f_name',type='string',requires = IS_NOT_EMPTY(),label=T('Name')),
    Field('f_file','upload', requires = IS_NOT_EMPTY(),label=T('Sequence Config Template')),
    auth.signature
    )
    
db.define_table('t_readme',
    Field('f_seq_config_id', type='reference t_seq_config',label=T('Seq Config ID')), 
    Field('f_run_name', type='string',label=T('Run Name')),
    Field('f_name', type='string',requires = IS_NOT_EMPTY(),label=T('Name')),
    Field('f_file','upload', requires = IS_NOT_EMPTY(),label=T('Readme file')),
    Field('f_excel_file','upload', requires = IS_NOT_EMPTY(),label=T('Readme file in excel')),
    Field('f_file_num',type='integer',label=T('Readme file Number')),
    Field('f_status', type='list:string',label=T('Status')),
    auth.signature
    )
    

## tables populated with a set of strings from seqconfigdb_populate.py

db.define_table( 't_read_type' ,
    Field('f_name', type='string',label=T('Name')),format='%(f_name)s')

db.define_table( 't_illumina' ,
    Field('f_name', type='string',label=T('Name')),format='%(f_name)s')

db.define_table( 't_illumina_snr' ,
    Field('f_name', type='string',label=T('Name')),format='%(f_name)s')
    
db.define_table( 't_barcodes' ,
    Field('f_barcode', type='string',unique=True,label=T('Barcode')),
    Field('f_sequence', type='string',label=T('Sequence')))

## constraints
db.t_seq_config_spreadsheets.f_run_name.requires = IS_NOT_IN_DB(db, db.t_seq_config_spreadsheets.f_run_name)
db.t_seq_config_spreadsheets.f_file.requires = IS_UPLOAD_FILENAME(extension = '(xls|xlsx)',error_message='Please upload an excel file') 

db.t_config_lane.f_seq_config_id.requires = IS_IN_DB(db, db.t_seq_config.id)
db.t_config_lane.f_qc_prod.default = 'QC'
db.t_config_lane.f_qc_prod.requires=IS_IN_SET(('QC','Production'))
db.t_config_lane.f_barcode.requires=IS_IN_DB(db,db.t_barcodes.f_barcode)
db.t_config_lane.f_lane_number.requires=IS_INT_IN_RANGE(1,9,error_message='lane numbers should be in the range 1 to 8') # 8 lanes on a single spreadsheet identified by a seq_config ID
db.t_config_lane.f_sample_number.requires=IS_INT_IN_RANGE(1,48,error_message='sample numbers should be in the range 1 to 48') # 48 samples per lane
db.t_config_lane.id.writable = db.t_config_lane.id.readable = False
#db.t_config_lane.f_seq_config_id.writable = db.t_config_lane.f_seq_config_id.readable = False

db.t_seq_config.f_read_type.requires = IS_IN_DB(db, db.t_read_type.f_name)
db.t_seq_config.f_illumina.requires = IS_IN_DB(db, db.t_illumina.f_name)
db.t_seq_config.f_illumina_snr.requires = IS_IN_DB(db, db.t_illumina_snr.f_name)
db.t_seq_config.f_run_name.requires = IS_IN_DB(db, db.t_seq_config_spreadsheets.f_run_name)
db.t_readme.f_run_name.requires = IS_IN_DB(db, db.t_seq_config_spreadsheets.f_run_name)

db.t_readme.f_status.requires=IS_IN_SET(('Waiting for Approval','Approved'))
db.t_readme.id.writable=db.t_readme.id.readable=False

db.t_seq_config.id.writable = db.t_seq_config.id.readable = False
db.t_seq_config.f_spsheet_id.writable = db.t_seq_config.f_spsheet_id.readable = False
db.t_seq_config_spreadsheets.id.writable = db.t_seq_config_spreadsheets.id.readable = False

#disable register link
if request.controller != 'appadmin':
  auth.settings.actions_disabled.append('register')
  
#add logger
import logging, logging.handlers
import os

def get_configured_logger(name):
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # This logger has no handlers, so we can assume it hasn't yet been configured
        # (Configure logger)
        
        formatter="%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
        handler = logging.handlers.RotatingFileHandler(os.path.join(request.folder,'private/app.log'),maxBytes=1024,backupCount=2)
        handler.setFormatter(logging.Formatter(formatter))

        handler.setLevel(logging.DEBUG)

        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Test entry:
        logger.debug(name + ' logger created')
    else:
        # Test entry:
        logger.debug(name + ' already exists')
    return logger

# Assign application logger to a global var  
logger = get_configured_logger(request.application)

# write contents of t_barcodes table on every update at  /home/www-data/web2py/applications/seqConfig/sequence_config_dir/ on lims server

db.t_barcodes._after_update.append(lambda s,f: writebarcodes(s,f))
db.t_barcodes._after_insert.append(lambda f,id: writebarcodes(f,id))
db.t_barcodes._after_delete.append(lambda s: writebarcodes(s))
def writebarcodes(*args):
    logger.debug('in write barcodes')
    try:
        filename='barcodes.txt'
        fname='applications/seqConfig/sequence_config_dir/'+filename
        f = open(fname, "w")
        
        rows =db(db.t_barcodes).select()
        strbarcodes=''
        for r in rows:
            if ( '+' not in str(r.f_barcode)):
                strbarcodes = strbarcodes + (str(r.f_barcode)) + '\t'+str(r.f_sequence)+ '\n'
        
        f.write(strbarcodes)
    finally:
          f.close()


          
#############---Tables for Track Samples---##########

db.define_table( 't_recentkeys' ,
    Field('f_bid', type='string',requires = IS_NOT_EMPTY(),label=T('Key/Bionimbus ID')),
    Field('f_firstname', type='string',label=T('First Name')),
    Field('f_lastname', type='string',label=T('Last Name')),
    Field('f_dategenerated', type='datetime',label=T('Key generated on')),
    Field('f_application', type='string',label=T('Application')),
    Field('f_project', type='string',label=T('Project'))
    )
