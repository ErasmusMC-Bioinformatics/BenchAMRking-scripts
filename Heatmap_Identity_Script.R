##Make the Heatmap graphs######
# Load necessary libraries
install.packages("gplots")
library(gplots)
library(RColorBrewer)


##Identity heatmap#########
##Entry file###
AMRacq <- read.csv(file = "You input identity file here", sep=",", header = TRUE)

# Prepare the data
gen <- AMRacq[-1]
row.names(gen) <- AMRacq$type
datag <- data.matrix(gen)
colnames(datag) <- gsub("_", " ", colnames(datag))

###Create heatmap#######
heatmap.2(datag, 
          main = "Heatmap of AMR Genes vs Tools", 
          xlab = "Tools", 
          ylab = "AMR Genes", 
          trace = "none", 
          margins = c(12, 9),  # Adjust these values as needed
          col = brewer.pal(8, "Dark2"), 
          density.info = "none", 
          Rowv = TRUE, 
          Colv = FALSE,
          labRow = rownames(datag))  # Make sure row names are included


###Binary file####
AMRacq <- read.csv(file = "You input binary file here", sep=",", header = TRUE)
gen <- AMRacq[-1]
row.names(gen) <- AMRacq$type
datag <- data.matrix(gen)
colnames(datag) <- gsub("_", " ", colnames(datag))
heatmap.2(datag, 
          main = "Heatmap of AMR Genes vs Tools", 
          xlab = "Tools", 
          ylab = "AMR Genes", 
          trace = "none", 
          margins = c(12, 9),  # Adjust these values as needed
          col = my_palette,  # Use the new color palette
#          breaks = breaks,  # Use the defined breaks
          density.info = "none", 
          Rowv = TRUE, 
          Colv = FALSE,
          labRow = rownames(datag),)  # Make sure row names are included.

####No legend####################
rownames(datag) <- gsub("_", " ", rownames(datag))
heatmap.2(datag, 
          main = "Heatmap of AMR Genes vs Tools", 
 #         xlab = "Tools", 
 #         ylab = "AMR Genes", 
          trace = "none", 
          margins = c(12, 9),  # Adjust these values as needed
          col = my_palette,  # Use the new color palette
          density.info = "none", 
          Rowv = TRUE, 
          Colv = FALSE,
          labRow = rownames(datag),  # Make sure row names are included.
          key = FALSE)  # No color key (legend)




