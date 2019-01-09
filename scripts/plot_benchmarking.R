library(dplyr)
library(ggplot2)
library(cowplot)

data <- read.table('benchmarking.txt', col.names=c('method','treesize','operatedsize','operation','time'))
data_means_se = data %>%
  group_by(method, treesize, operation, operatedsize) %>%
  summarize(mean_time=1000*mean(time),
            sd_time=sd(time),
            n_time=n(),
            se_time=sd_time/sqrt(n_time),
            se_upper=mean_time+1000*se_time,
            se_lower=mean_time-1000*se_time)

p <- ggplot(data_means_se, aes(x=treesize,y=mean_time, color=method)) + geom_line() + geom_point(size=.1) +
  geom_errorbar(aes(ymin=se_lower,ymax=se_upper), width=.3)  +
  xlab("TreeSize") + ylab("Time (ms)") +
  facet_grid(~operation)

ggsave(p, file='benchmarking.png')
