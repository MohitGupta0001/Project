Interview Tasks Project 🚀

This repository contains implementations of three interview tasks demonstrating skills in API integration, file handling, and risk evaluation.

Tasks Overview:

Movie Scrubber 🎬

Fetches movies released in the last 2 months with a rating greater than 4.

Displays results in a card layout with movie name and rating.

Features a single-page interface with a Scrub button and loading indicator.

Drive File Checker 📂

Scans a directory or drive to search for files by type (PDF, Word, etc.) and keywords in the file name.

Lists matching files with their name and path.

Allows users to open files directly from the results.

Company Risk Evaluator 🏢

Evaluates company risk based on news sentiment and attached PDF balance sheets.

If news is negative → shows High Risk, if positive → shows Low Risk.

Checks attached PDF for the word “Balance Sheet” and adjusts risk accordingly.

Displays Average Risk considering both news and PDF analysis.

Only PDF attachments are allowed.

Technologies Used:

Python 3.14, 
Requests, PyPDF2 (for PDF handling), python-docx (optional for Word files)

External APIs: Movie database API , News API

Note: All tasks are modular and can be run independently.
