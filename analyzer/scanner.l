%option noyywrap 
%{
#include "parser.tab.h"
#include <string.h>

int line_num = 1;
%}

%%
"rm -rf"                { yylval.str = strdup("dangerous_command"); return THREAT; }
"sudo"                  { yylval.str = strdup("privilege_escalation"); return THREAT; }
"nc -e"|"bash -i"       { yylval.str = strdup("reverse_shell"); return THREAT; }

([0-9]{1,3}\.){3}[0-9]{1,3} {
    yylval.str = strdup("suspicious_ip");
    return THREAT;
}

"Failed password"       { yylval.str = strdup("brute_force_attempt"); return THREAT; }
"error"                 { yylval.str = strdup("error_log"); return THREAT; }

\n { line_num++; }

. ;
%%