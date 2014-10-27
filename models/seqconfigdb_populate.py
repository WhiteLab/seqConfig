from gluon.contrib.populate import populate
##if db(db.t_seq_config).isempty():
  ##   populate(db.t_seq_config,10)
     
##if db(db.t_config_lane).isempty():
  ##   populate(db.t_config_lane,100)
     
##if db(db.t_seq_config_spreadsheets).isempty():
  ##   populate(db.t_seq_config_spreadsheets,10)
#db.t_seq_config_spreadsheets.truncate()
#db.t_seq_config.truncate()
#db.t_config_lane.truncate()
#db.t_barcodes.truncate()

if db(db.t_read_type).isempty():
      db.t_read_type.insert( f_name = 'single-end' )
      db.t_read_type.insert( f_name = 'paired-end' )
      
      
if db(db.t_illumina).isempty():
      db.t_illumina.insert( f_name = 'HiSeq2000' )
      db.t_illumina.insert( f_name = 'MiSeq' )
      
if db(db.t_illumina_snr).isempty():
    db.t_illumina_snr.insert( f_name = '300146' )
    db.t_illumina_snr.insert( f_name = '300279' )
    db.t_illumina_snr.insert( f_name = '300137' )
    db.t_illumina_snr.insert( f_name = '300552' )
    db.t_illumina_snr.insert( f_name = 'HiSeq2000-1' )
    db.t_illumina_snr.insert( f_name = 'HiSeq2000-2' )
    db.t_illumina_snr.insert( f_name = 'HiSeq2000-3' )
    db.t_illumina_snr.insert( f_name = 'HiSeq2000-4' )
    db.t_illumina_snr.insert( f_name = 'MiSeq-M00834' )
    
if db(db.t_barcodes).isempty():
    for i in range(1,24):
        s='IL-'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    db.t_barcodes.insert( f_barcode = 'IL-25')
    db.t_barcodes.insert( f_barcode = 'IL-27')
    
    for i in range(1,229):
        s='TS'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    for i in range(501,509):
        s='N'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    for i in range(701,713):
        s='N'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    for i in range(501,509):
        s='A'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    for i in range(701,713):
        s='A'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    for i in range(1,13):
        s='PE'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    for i in range(1,17):
        s='L2DR-BC'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
    for i in range(1,97):
        s='HP'+str(i)
        db.t_barcodes.insert( f_barcode = s)
        
        
 #Dual indexed barcodes
  #N+A
        
    for i in range(501,509):
        for j in range(501,509):
            s='N'+str(i) + '+' + 'A'+str(j)
            db.t_barcodes.insert( f_barcode = s)
        
        for j in range(701,713):
            s='N'+str(i) + '+' + 'A'+str(j)
            db.t_barcodes.insert( f_barcode = s)
        
        
    for i in range(701,713):
        for j in range(501,509):
            s='N'+str(i) + '+' + 'A'+str(j)
            db.t_barcodes.insert( f_barcode = s)
        
        for j in range(701,713):
            s='N'+str(i) + '+' + 'A'+str(j)
            db.t_barcodes.insert( f_barcode = s)
        
 #A+N
        
    for i in range(501,509):
        for j in range(501,509):
            s='A'+str(i) + '+' + 'N'+str(j)
            db.t_barcodes.insert( f_barcode = s)
        
        for j in range(701,713):
            s='A'+str(i) + '+' + 'N'+str(j)
            db.t_barcodes.insert( f_barcode = s)
        
        
    for i in range(701,713):
        for j in range(501,509):
            s='A'+str(i) + '+' + 'N'+str(j)
            db.t_barcodes.insert( f_barcode = s)
        
        for j in range(701,713):
            s='A'+str(i) + '+' + 'N'+str(j)
            db.t_barcodes.insert( f_barcode = s)
