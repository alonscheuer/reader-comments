library(tidyverse)
library(quanteda)
library(quanteda.textstats)
library(ggpubr)


data <- read_csv("spans_inferred.csv") %>%
    filter(work != "/works/30346350") %>%
    mutate(additional_functions = str_replace_all(additional_functions, "[\\[\\]' ]", ""),
           additional_entities = str_replace_all(additional_entities, "[\\[\\]' ]", "")) %>%
    mutate(prediction = paste(prediction, additional_functions, sep = ","),
           entities = paste(entities, additional_entities, sep = ";")) %>%
    mutate(entities = str_split(entities, ";")) %>%
    mutate(entities = as.character(lapply(entities, function(x) paste(x[which(x != "NA")], collapse = ";")))) %>%
    mutate(prediction = str_remove_all(prediction, "(,NA|,none|none,[^N]|,$)")) %>%
    select(-additional_functions, -additional_entities) %>%
    separate_longer_delim(cols = prediction, delim = ",") %>%
    mutate(docid = row_number()) %>%
    mutate(maskedText = tolower(maskedText))


# TTR

cor <- data %>% corpus(docid_field = "docid", text_field = "hasText")
cor <- corpus_group(cor, groups = data$prediction)
tok <- tokens(cor)
ntok <- ntoken(tok)
ttr <- textstat_lexdiv(tok)
ttr$ntok <- ntok
print(ttr)
cor.test(ttr$TTR, ttr$ntok)

# PREDICTION COUNTS

data %>%
    group_by(work, prediction) %>%
    summarise(ncomments = length(unique(partOf)), nspans = n()) %>%
    pivot_wider(names_from = work, values_from = starts_with("n"), values_fill = 0) %>% write_csv("pred_counts.csv")

# THREAD LABEL COUNTS

data %>%
    group_by(inThread, prediction) %>%
    summarise(n = length(unique(partOf))) %>%
    pivot_wider(names_from = prediction, values_from = n, values_fill = 0) %>%
    write_csv("thread_funcs.csv")

data %>%
    group_by(inThread, prediction) %>%
    summarise(n = length(unique(partOf))) %>%
    group_by(prediction) %>%
    summarise(mean = mean(n), sd = sd(n), p2 = round(sum(n >= 2)/n(),2), p4 = round(sum(n >= 4)/n(),2)) %>%
    filter(prediction != "none") %>%
    arrange(prediction)

# FUNCTION DISTRIBUTION OVER CHAPTERS

p <- data %>%
    group_by(work, chapter, prediction) %>%
    summarise(n = n()) %>%
    filter(prediction %in% c("interpretation", "emotion", "feedback", "community_interaction", "personal_story")) %>%
    mutate(prediction = factor(prediction, levels = c("emotion", "interpretation", "feedback", "community_interaction", "personal_story"))) %>%
    ggline(x = "chapter", y = "n", color = "prediction", plot_type = "l") %>%
    facet(facet.by = c("work", "prediction"), scales = "free", panel.labs = list(work = c("Fic 1", "Fic 3"), prediction = c("emotion", "interpretation", "feedback", "comm. interaction", "personal story"))) +
    rremove("x.text") +
    rremove("x.ticks") +
    rremove("legend")
ggexport(p, filename="progress.pdf", height = 4)
