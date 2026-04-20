%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int line_num;
extern FILE *yyin;

void yyerror(const char *s);
void add_threat(const char* type);
%}

%union {
    char* str;
}

%token <str> THREAT

%%

input:
    input THREAT {
        add_threat($2);
        free($2);
    }
    |
    ;

%%

int first = 1;

void add_threat(const char* type) {
    if (first) {
        printf("{\"threats\":[\n");
        first = 0;
    } else {
        printf(",\n");
    }
    printf("{\"type\":\"%s\",\"line\":%d}", type, line_num);
}

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *file = fopen(argv[1], "r");
        if (!file) {
            perror("File open failed");
            return 1;
        }
        yyin = file;
    }

    yyparse();

    if (!first)
        printf("\n]}\n");
    else
        printf("{\"threats\":[]}\n");

    return 0;
}

void yyerror(const char *s) {
    fprintf(stderr, "Parse error: %s at line %d\n", s, line_num);
}