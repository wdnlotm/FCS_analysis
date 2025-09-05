#Run this by
# SIF=/project/iprime_storage/myles_kim/imageD/R441_cytof/rstudio_R443_v6.sif
# apptainer exec $SIF Rscript cycombine_simple.r datafile markerfile savefile

library(cyCombine)
library(tidyverse)
library('data.table')

args <- commandArgs(trailingOnly=TRUE)

data_file <- args[1]
marker_file <- args[2]
batchcorrected_file <- args[3]

# fcs_dt <-  fread("fcs_df_trimmed_transformed_w_custom_cf.csv.gz") %>% data.frame()
fcs_data <- read_csv(data_file) %>% data.frame()
head(fcs_data)

lines <- readLines(marker_file)
markers_2_use <- lines
markers_2_use

corrected <- batch_correct(
  df = fcs_data,
  # covar = "condition",
  markers = markers_2_use,
  norm_method = "scale", # "rank" is recommended when combining data with heavy batch effects
  rlen = 19, # Higher values are recommended if 10 does not appear to perform well
  seed = 1234, # Recommended to use your own random seed
  # anchor = "anchor"
)

head(corrected %>% data.frame())
# write_csv(corrected, batchcorrected_file)

# added
gz_connection <- gzfile(batchcorrected_file, "w")
# Write the dataframe to the connection
write.csv(corrected, gz_connection, row.names = FALSE)
# Close the connection
close(gz_connection)
