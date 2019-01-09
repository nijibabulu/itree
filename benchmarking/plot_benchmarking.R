library(dplyr)
library(ggplot2)
library(cowplot)
library(ggthemes)

data <- read.table('benchmarking.txt', col.names=c('method','treesize','operatedsize','operation','time'))
data_means_se = data %>%
  group_by(method, treesize, operation, operatedsize) %>%
  summarize(mean_time=1000*mean(time),
            sd_time=sd(time),
            n_time=n(),
            se_time=sd_time/sqrt(n_time),
            se_upper=mean_time+1000*se_time,
            se_lower=mean_time-1000*se_time)
data_means_se$ktreesize = data_means_se$treesize/1000
data_means_se$method = factor(as.character(data_means_se$method), levels=c('itree','intervaltree','naive'))

p <- ggplot(data_means_se, aes(x=ktreesize,y=mean_time, color=method)) + geom_line() + geom_point(size=.1) +
  geom_errorbar(aes(ymin=se_lower,ymax=se_upper), width=.03)  +
  xlab("TreeSize, k") + ylab("Time (ms)") +
  facet_grid(~operation) +
  theme(legend.title = element_blank(), legend.position = 'top', legend.justification = 0.5) +
  scale_y_log10() +
  scale_x_continuous(breaks=c(0,5,10), limits=c(0,10)) +
  scale_color_ptol()
p

ggsave(p, file='benchmarking.png', width=6, height=4)
