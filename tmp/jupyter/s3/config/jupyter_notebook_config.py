c.Application.log_level = 'DEBUG'
c.NotebookApp.contents_manager_class = 's3nb.S3ContentsManager'
c.S3ContentsManager.s3_base_uri = 's3://jorgemarsal-notebook/'
