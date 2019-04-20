#include <iostream>

using namespace std;

struct CompileArguments
{
    bool shouldKeepCPP = false;
    bool isOutputSpecified = false;
    string myplFile = "";
    string outputFilename = "";
};

static const string CMD_TRANSLATE_START = "python hw7.py ";
static const string CMD_COMPILE_CPP_START = "g++ __translated_source.cpp ";
static const string CMD_RM_CPP = "rm __translated_source.cpp";

static void execute(string);
static void parseArguments(CompileArguments *, int, char **);
static void usageError(string);
static bool isMyPLFiletype(string);


int main(int argc, char **argv)
{
    CompileArguments settings;
    parseArguments(&settings, argc, argv);

    string translateCommand = CMD_TRANSLATE_START + settings.myplFile;
    execute(translateCommand);

	string compileCommand = CMD_COMPILE_CPP_START;
	if (settings.isOutputSpecified) 
		compileCommand += "-o " + settings.outputFilename;
	

	execute(compileCommand);

	if (!settings.shouldKeepCPP) 
		execute(CMD_RM_CPP);
	

    return 0;
}

void execute(string cmd){
	system(cmd.c_str());
}

void parseArguments(CompileArguments *settings, int argc, char **argv)
{
    if (argc <= 1)
    {
        usageError("Error: Insufficient arguments.");
    }

    if (!isMyPLFiletype(argv[1]))
    {
        usageError("Error: First argument must be .mypl file.");
    }

    settings->myplFile = argv[1];

    string arg;
    for (int i = 2; i < argc; i++)
    {
        arg = argv[i];

        if (arg.compare("-o") == 0)
        {
            settings->isOutputSpecified = true;
            if (i + 1 == argc)
            {
                usageError("Error: Output specifier '-o' given, but no filename provided.");
            }

            settings->outputFilename = argv[i + 1];
        }
        else if (arg.compare("-keep") == 0 || arg.compare("-k") == 0)
        {
            settings->shouldKeepCPP = true;
        }
    }
}

void usageError(string msg)
{
    cout << msg << endl;
    cout << "Usage: mplc filename [-o executableName] [-keep]" << endl;
    exit(EXIT_FAILURE);
}

bool isMyPLFiletype(string str)
{
    return str.size() > 4 && (str.compare(str.size() - 4, 4, "mypl") == 0);
}
