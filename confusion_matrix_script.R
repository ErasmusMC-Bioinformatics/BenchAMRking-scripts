my.plotcorr <- function (corr, outline = FALSE, col = "grey", upper.panel = c("ellipse", "number", "none"), lower.panel = c("ellipse", "number", "none"), diag = c("none", "ellipse", "number"), digits = 2, bty = "n", axes = FALSE, xlab = "", ylab = "", asp = 1, cex.lab = par("cex.lab"), cex = 0.75 * par("cex"), mar = 0.1 + c(2, 2, 4, 2), ...)
{
  # this is a modified version of the plotcorr function from the ellipse package
  # this prints numbers and ellipses on the same plot but upper.panel and lower.panel changes what is displayed
  # diag now specifies what to put in the diagonal (numbers, ellipses, nothing)
  # digits specifies the number of digits after the . to round to
  # unlike the original, this function will always print x_i by x_i correlation rather than being able to drop it
  # modified by Esteban Buz
  if (!require('ellipse', quietly = TRUE, character = TRUE)) {
    stop("Need the ellipse library")
  }
  savepar <- par(pty = "s", mar = mar)
  on.exit(par(savepar))
  if (is.null(corr))
    return(invisible())
  if ((!is.matrix(corr)) || (round(min(corr, na.rm = TRUE), 6) < -1) || (round(max(corr, na.rm = TRUE), 6) > 1))
    stop("Need a correlation matrix")
  plot.new()
  par(new = TRUE)
  rowdim <- dim(corr)[1]
  coldim <- dim(corr)[2]
  rowlabs <- dimnames(corr)[[1]]
  collabs <- dimnames(corr)[[2]]
  if (is.null(rowlabs))
    rowlabs <- 1:rowdim
  if (is.null(collabs))
    collabs <- 1:coldim
  rowlabs <- as.character(rowlabs)
  collabs <- as.character(collabs)
  col <- rep(col, length = length(corr))
  dim(col) <- dim(corr)
  upper.panel <- match.arg(upper.panel)
  lower.panel <- match.arg(lower.panel)
  diag <- match.arg(diag)
  cols <- 1:coldim
  rows <- 1:rowdim
  maxdim <- max(length(rows), length(cols))
  plt <- par("plt")
  xlabwidth <- max(strwidth(rowlabs[rows], units = "figure", cex = cex.lab))/(plt[2] - plt[1])
  xlabwidth <- xlabwidth * maxdim/(1 - xlabwidth)
  ylabwidth <- max(strwidth(collabs[cols], units = "figure", cex = cex.lab))/(plt[4] - plt[3])
  ylabwidth <- ylabwidth * maxdim/(1 - ylabwidth)
  plot(c(-xlabwidth - 0.5, maxdim + 0.5), c(0.5, maxdim + 1 + ylabwidth), type = "n", bty = bty, axes = axes, xlab = "", ylab = "", asp = asp, cex.lab = cex.lab, ...)
  text(rep(0, length(rows)), length(rows):1, labels = rowlabs[rows], adj = 1, cex = cex.lab)
  text(cols, rep(length(rows) + 1, length(cols)), labels = collabs[cols], srt = 90, adj = 0, cex = cex.lab)
  mtext(xlab, 1, 0)
  mtext(ylab, 2, 0)
  mat <- diag(c(1, 1))
  plotcorrInternal <- function() {
    if (i == j){ #diag behavior
      if (diag == 'none'){
        return()
      } else if (diag == 'number'){
        text(j + 0.3, length(rows) + 1 - i, round(corr[i, j], digits=digits), adj = 1, cex = cex)
      } else if (diag == 'ellipse') {
        mat[1, 2] <- corr[i, j]
        mat[2, 1] <- mat[1, 2]
        ell <- ellipse(mat, t = 0.43)
        ell[, 1] <- ell[, 1] + j
        ell[, 2] <- ell[, 2] + length(rows) + 1 - i
        polygon(ell, col = col[i, j])
        if (outline)
          lines(ell)
      }
    } else if (i >= j){ #lower half of plot
      if (lower.panel == 'ellipse') { #check if ellipses should go here
        mat[1, 2] <- corr[i, j]
        mat[2, 1] <- mat[1, 2]
        ell <- ellipse(mat, t = 0.43)
        ell[, 1] <- ell[, 1] + j
        ell[, 2] <- ell[, 2] + length(rows) + 1 - i
        polygon(ell, col = col[i, j])
        if (outline)
          lines(ell)
      } else if (lower.panel == 'number') { #check if ellipses should go here
        text(j + 0.3, length(rows) + 1 - i, round(corr[i, j], digits=digits), adj = 1, cex = cex)
      } else {
        return()
      }
    } else { #upper half of plot
      if (upper.panel == 'ellipse') { #check if ellipses should go here
        mat[1, 2] <- corr[i, j]
        mat[2, 1] <- mat[1, 2]
        ell <- ellipse(mat, t = 0.43)
        ell[, 1] <- ell[, 1] + j
        ell[, 2] <- ell[, 2] + length(rows) + 1 - i
        polygon(ell, col = col[i, j])
        if (outline)
          lines(ell)
      } else if (upper.panel == 'number') { #check if ellipses should go here
        text(j + 0.3, length(rows) + 1 - i, round(corr[i, j], digits=digits), adj = 1, cex = cex)
      } else {
        return()
      }
    }
  }
  for (i in 1:dim(corr)[1]) {
    for (j in 1:dim(corr)[2]) {
      plotcorrInternal()
    }
  }
  invisible()
}


#usage of my.plotcorr
#much like the my.plotcorr function, this is modified from the plotcorr documentation
#this function requires the ellipse library, though, once installed you don't need to load it - it is loaded in the function
#install.packages(c('ellipse'))
#library(ellipse)
install.packages("ellipse")
#source('my.plotcorr.R')
# Load your data from the CSV file
data <- read.csv("Add file here ")
# Exclude non-numeric columns (e.g., first column)
numeric_data <- data[, -1]

# Create the correlation matrix
corr.amr<- cor(numeric_data)


# Standard plot, all ellipses are grey, nothing is put in the diagonal
my.plotcorr(corr.amr)

# Here we play around with the colors, colors are selected from a list with colors recycled
# Thus to map correlations to colors we need to make a list of suitable colors
# To start, pick the end (and mid) points of a scale, here a red to white to blue for neg to none to pos correlation
colsc=c(rgb(241, 54, 23, maxColorValue=255), 'white', rgb(0, 61, 104, maxColorValue=255))

# Build a ramp function to interpolate along the scale, I've opted for the Lab interpolation rather than the default rgb, check the documentation about the differences
colramp = colorRampPalette(colsc, space='Lab')

# I'll show two types of color styles using this color ramp
# the first
# Use the same number of colors along the scale for the number of variables
colors = colramp(length(corr.amr[1,]))

# then plot an example with only ellipses, without a diagonal and with a main title
# the color selection stuff here multiplies the correlations such that they can index individual colors and create a sufficiently large list
# incase you are confused, r allows vector indexing with non-integers by rounding down, i.e. colors[1.8] == colors[1]
my.plotcorr(corr.amr, col=colors[5*corr.amr + 6], main='Predictor correlations')

# the second form
# we could, alternatively, make a scale with 100 points
colors = colramp(100)
# then pick colors along this 100 point scale given the correlation value * 100 rounded down to the nearest integer
# to do that we need to move the correlation range from [-1, 1] to [0, 100]
# now plot again with ellipses along the diagonal
my.plotcorr(corr.amr, col=colors[((corr.amr + 1)/2) * 100], diag='ellipse', main='Predictor correlations')

# or, add numbers to the bottom of the chart
my.plotcorr(corr.amr, col=colors[((corr.amr + 1)/2) * 100], diag='ellipse', lower.panel="number", main='Predictor correlations')

# or, switch the numbers and ellipses and reduce the margins
my.plotcorr(corr.amr, col=colors[((corr.amr + 1)/2) * 100], diag='ellipse', upper.panel="number", mar=c(0,2,0,0), main='Predictor correlations')

# or, drop the diagonal and numbers
my.plotcorr(corr.amr, col=colors[((corr.amr + 1)/2) * 100], upper.panel="none", mar=c(0,2,0,0), main='Predictor correlations')


