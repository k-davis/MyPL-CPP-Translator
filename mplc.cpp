#include <iostream>

using namespace std;

struct compileSettings
{
    bool shouldKeepCPP = false;
    bool isOutputSpecified = false;
    string myplFile = "";
    string outputFilename = "";
};

void printSettings(compileSettings);
void parseArguments(compileSettings *, int, char **);
void usageError(string);
bool isMyPLFiletype(string);

int main(int argc, char **argv)
{
    compileSettings settings;
    parseArguments(&settings, argc, argv);
    //printSettings(settings);

    string command = "python transpile.py ";
    command += settings.isOutputSpecified ? settings.outputFilename : "";

    system(command.c_str());

    return 0;
}

void printSettings(compileSettings settings)
{
    cout << "shouldKeepCPP: " << settings.shouldKeepCPP << endl;
    cout << "isOutputSpecified: " << settings.isOutputSpecified << endl;
    cout << "myplFile: " << settings.myplFile << endl;
    cout << "outputFilename: " << settings.outputFilename << endl;
}

void parseArguments(compileSettings *settings, int argc, char **argv)
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