using TMPro;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class LoginManager : MonoBehaviour
{
    public TMP_InputField usernameInput;
    public TMP_InputField passwordInput;
    public TMP_Dropdown scriptSelector;
    public TMP_Dropdown camaraSelector;
    public TMP_InputField ipInputField;

    public void OnStartButtonPressed()
    {
        string username = usernameInput.text;
        string password = passwordInput.text;
        string script = scriptSelector.options[scriptSelector.value].text;
        string camOption = camaraSelector.options[camaraSelector.value].text;

        Debug.Log($"Usuario: {username}, Contraseña: {password}, Script: {script}");

        // Guardar en PlayerPrefs para usar en la siguiente escena
        PlayerPrefs.SetString("username", username);
        PlayerPrefs.SetString("password", password);
        PlayerPrefs.SetString("script", script);
        PlayerPrefs.SetString("camOption", camOption);

        if (camOption == "DroidCam")
        {
            string droidcamIP = ipInputField.text;
            PlayerPrefs.SetString("droidcamIP", droidcamIP);
        }

        // Cargar la escena de cámara (a crear más adelante)
        SceneManager.LoadScene("CamaraScene");
    }
}
