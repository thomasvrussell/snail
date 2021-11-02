library(fpca)
getwd()

args <- commandArgs(TRUE)
InputCSV <- args[1]
OutputCSV <- args[2]

DATA <- read.csv(InputCSV)
DATA <- apply(DATA, 2, as.numeric)

ReqGrid <- read.csv("B0_ReqGrid.csv")
ReqGrid <- as.numeric(ReqGrid$x)

SoFittedMean <- read.csv("B0_SoFittedMean.csv")
SoFittedMean <- apply(SoFittedMean, 2, as.numeric)

SoEval <- read.csv("B0_SoEval.csv")
SoEval <- as.numeric(SoEval$x)

SoEfunc <- read.csv("B0_SoEfunc.csv")
SoEfunc <- apply(SoEfunc, 2, as.numeric)

SoErrvar <- read.csv("B0_SoErrvar.csv")
SoErrvar <- as.numeric(SoErrvar$x[1])

r <- 90
fpcs <- fpca.score(DATA, ReqGrid, SoFittedMean, SoEval, SoEfunc, SoErrvar, r)
write.csv(fpcs, file=OutputCSV, row.names=F, quote=F)
