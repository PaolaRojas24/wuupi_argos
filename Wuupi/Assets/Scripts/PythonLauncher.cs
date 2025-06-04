using UnityEngine;
using System.Diagnostics;
using System.IO;

public class PythonLauncher : MonoBehaviour
{
    private Process pythonProcess;

    void Start()
    {
        string username = PlayerPrefs.GetString("username");
        string password = PlayerPrefs.GetString("password");
        string selection = PlayerPrefs.GetString("script"); // "Manos" o "Piernas"
        string camOption = PlayerPrefs.GetString("camOption"); // "Integrada" o "DroidCam"
        string droidcamIP = PlayerPrefs.GetString("droidcamIP", ""); // Puede estar vacío
        string pythonPath = "python"; // Cambiar por ruta completa si es necesario

        string scriptPath = "";

        if (selection == "Manos")
            scriptPath = Path.Combine(Application.dataPath, "Python", "manos_argos.py");
        else if (selection == "Piernas")
            scriptPath = Path.Combine(Application.dataPath, "Python", "piernas_argos.py");
        else
            UnityEngine.Debug.LogError("Opción no reconocida en el dropdown: " + selection);
    string args = $"\"{scriptPath}\" \"{username}\" \"{password}\" \"{camOption}\" \"{droidcamIP}\"";

        ProcessStartInfo psi = new ProcessStartInfo
        {
            FileName = pythonPath,
            Arguments = args,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };

        pythonProcess = new Process { StartInfo = psi };
        pythonProcess.OutputDataReceived += (sender, e) => UnityEngine.Debug.Log("[PYTHON OUT] " + e.Data);
        pythonProcess.ErrorDataReceived += (sender, e) => UnityEngine.Debug.LogError("[PYTHON ERR] " + e.Data);

        try
        {
            pythonProcess.Start();
            pythonProcess.BeginOutputReadLine();
            pythonProcess.BeginErrorReadLine();
        }
        catch (System.Exception ex)
        {
            UnityEngine.Debug.LogError("Error al lanzar Python: " + ex.Message);
        }
    }

    void OnApplicationQuit()
    {
        if (pythonProcess != null && !pythonProcess.HasExited)
        {
            pythonProcess.Kill();
        }
    }
}
