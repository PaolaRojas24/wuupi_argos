using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class CameraSelector : MonoBehaviour
{
    public TMP_Dropdown cameraDropdown;
    public TMP_InputField ipInputField;
    public TMP_Text ipLabelText;

    void Start()
    {
        cameraDropdown.onValueChanged.AddListener(OnDropdownChanged);
        OnDropdownChanged(cameraDropdown.value); // Actualiza la visibilidad al iniciar
    }

    void OnDropdownChanged(int index)
    {
        string selected = cameraDropdown.options[index].text;

        bool useIP = selected == "DroidCam";
        ipInputField.gameObject.SetActive(useIP);
        ipLabelText.gameObject.SetActive(useIP);
    }
}