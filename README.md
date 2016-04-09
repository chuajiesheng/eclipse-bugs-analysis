# Eclipse Bug Analysis

## Introduction

Referring to [1], labelling the priority of bugs is still a manual processing.
This repository aims to improve the feature extraction techniques describe in the paper.

## How the extraction is done

1. Retrieve a list of XML bugs report from the `data/huge-eclipse-xml-reports` folder (each contains 100 bugs)
2. Parse the files and read into memory as Bug objects
3. Generate different statistics for the data we have
   (distribution of priority, authors assigned to fix the bugs)
4. Using a step of 15,000, we fork multiple process to extract the features
   (since the bugs have been read into memory and will not change, we can safely fork this
    1. Extract the all the features (listed in the features section)
    2. Output the feature to `run/features_<run_id>_<start_index>to<end_index>.txt`

## Features

    Temporal Factor

    1. number of comments (short_desc) within 5 days
    2. number of bugs reported within 7 days before the reporting of bug report
    3. number of bugs reported with the same severity within 7 days before the reporting of bug report
    4. number of bugs reported with the same or higher severity within 7 days before the reporting of bug report
    5. same as 2, but for 30 days
    6. same as 3, but for 30 days
    7. same as 4, but for 30 days
    8. same as 2, but for 1 days
    9. same as 3, but for 1 days
    10. same as 4, but for 1 days
    11. same as 2, but for 3 days
    12. same as 3, but for 3 days
    13. same as 4, but for 3 days

    Author Factor

    14. mean priority of bugs the author fixed
    15. median priority of bugs the author fixed
    16. mean priority of all bug reports made by the author of bug report prior to the reporting of bug report
    17. median priority of all bug reports made by the author of bug report prior to the reporting of bug report
    18. the number of bug reports made by the author of bug report prior to the reporting of bug report

    Related-Report Factor

    19. operating system (29 different operating system) (from 19 to 48 inclusive, 1 empty)

    49. mean priority of top 20 most similar document by cosine similarity and tf-idf
    50. median priority of top 20 most similar document by cosine similarity and tf-idf

    51. mean priority of top 10 most similar document by cosine similarity and tf-idf
    52. median priority of top 10 most similar document by cosine similarity and tf-idf

    53. mean priority of top 5 most similar document by cosine similarity and tf-idf
    54. median priority of top 5 most similar document by cosine similarity and tf-idf

    55. mean priority of top 3 most similar document by cosine similarity and tf-idf
    56. median priority of top 3 most similar document by cosine similarity and tf-idf

    57. mean priority of top 1 most similar document by cosine similarity and tf-idf
    58. median priority of top 1 most similar document by cosine similarity and tf-idf

    Severity Factor

    59. severity (7 different severity) (from 59 to 66 inclusive, 1 empty)

    Product Factor

    67. product (76 different product) (from 67 to 143 inclusive, 1 empty)
    144. number of bug reports made for the same product as that of bug report prior to the reporting of bug report
    145. number of bug reports made for the same product of the same severity as that of bug report prior to the reporting of bug report
    146. number of bug reports made for the same product of the same or higher severity as those of bug report prior to those reporting of bug report
    147. proportion of bug reports made for the same product as that of bug report prior to the reporting of bug report that are assigned priority P1.
    148. same as 144, but for priority P2.
    149. same as 144, but for priority P3.
    150. same as 144, but for priority P4.
    151. same as 144, but for priority P5.
    152. mean priority of bug reports made for the same product as that of BR prior to the reporting of BR
    153. Median priority of bug reports made for the same product as that of BR prior to the reporting of BR

    Component Factor

    154. component (487 different components) (from 154 to 641 inclusive, 1 empty)
    642. number of bug reports made for the same component as that of BR prior to the reporting of BR
    643. number of bug reports made for the same component of the same severity as that of BR prior to the reporting of BR
    644. number of bug reports made for the same component of the same or higher severity as those of BR prior to the # reporting of BR
    645. proportion of bug reports made for the same component as that of BR prior to the reporting of BR that are assigned priority P1.
    646. same as 641, but for priority P2.
    647. same as 641, but for priority P3.
    648. same as 641, but for priority P4.
    649. same as 641, but for priority P5.
    650. mean priority of bug reports made for the same component as that of BR prior to the reporting of BR
    651. median priority of bug reports made for the same component as that of BR prior to the reporting of BR

    652. empty

## What is in this repository

1. bug.py - the bug object model used to extract information about each bug report from the XML and provide function to calculate feature with reference to itself
2. feature_extraction.py - feature extraction script which process and extract feature from each of the bugs.

## Reference

[1] [DRONE: Predicting Priority of Reported Bugs by Multi-factor Analysis](http://www.mysmu.edu/faculty/davidlo/papers/icsm13-priority.pdf)