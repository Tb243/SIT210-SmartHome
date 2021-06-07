#!/usr/bin/python3

import paho.mqtt.client as mqtt
import PySimpleGUI as sg
import time
from threading import Timer
import os
#MQTT broker/server - running on this pi so localhost this time
mqttBroker = "localhost"
#two clients - could be implemented as 1 with the message split into temp//tempstatus
client = mqtt.Client("temperature")
client1 = mqtt.Client("studystatus")
#connect both clients to broker
client.connect(mqttBroker)
client1.connect(mqttBroker)
client.loop_start()
client1.loop_start()

#subscribe to the published topics from each area
client.subscribe("temp")
client1.subscribe("tempstatus")

#define/declare variables
statusc = "NULL"
#time in seconds for temperature reading on pi to *timeout*
timeout = 5
global temp
global tempcstat
tempcstat = False
temp = False
tempc = 0
timesinceupdate = time.time()

def on_message(client, userdata, message):
    global tempc
    global timesinceupdate
    rawtemp = str(message.payload.decode("utf-8"))
    if(rawtemp != "nan"):
        rawtemp = float(rawtemp)
        tempc = "{:.1f}".format(rawtemp)

        timesinceupdate = time.time()

def on_message1(client1, userdata, message):
    global statusc
    statusc = str(message.payload.decode("utf-8"))

client.on_message = on_message
client1.on_message = on_message1

#uncomment this line to view available themes for gui window *on large monitor!*
#sg.theme_previewer()

def main():
    #define buttons and text windows here
    title = sg.T('Smart Home Hub', size=(20,1), font=('Arial', 16), justification='l', pad=((145,0), (0, 50)))
    toggleheat = sg.B('', image_data=toggle_btn_off, key='-TOGGLE-GRAPHIC-', button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)
    togglelight = sg.B('', image_data=toggle_btn_off, key='-TOGGLE-GRAPHIC1-', button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)
    studyheatlabel = sg.T('Study Heater', font=('Arial', 16))
    outsidelightlabel= sg.T('Outside Lights', font=('Arial', 16))
    reboot = sg.B('      ', image_data=Bomb, key='-REBOOT-', border_width=0)
    studytemp = sg.T('Study Temperature: '), sg.T(' '*2), sg.Text(size=(8,1), key='-TEMP-', font=('Arial', 24))
    close = sg.B('Exit', image_data=Abort, key='-CLOSE-', border_width=0)
    closelabel = sg.T('Exit program', pad=(5,0))
    rebootlabel = sg.T('Reboot', pad=(18,0))

    #define layout from elements defined above
    layout = [[title],
              [studytemp],
              [toggleheat, studyheatlabel],
              [togglelight, outsidelightlabel],
              [reboot, close],
              [rebootlabel, closelabel]]

    window = sg.Window('Hub', layout, size=(480,320), finalize=True)
    window.Maximize()
    graphic_off = True
    graphic1_off = True
    def toggle_heat_func():
        if(statusc =="dc"):
            window['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_off)
            graphic_off = True
        if(statusc == "HeatOn"):
            window['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_on)
            graphic_off = False
        elif(statusc == "HeatOff"):
            window['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_off)
            graphic_off = True

    while True:             # Event Loop

        event, values = window.read(timeout=200)

        #update the GUI interface with current study temp
        window['-TEMP-'].update(str(tempc) + '°c')

        #event handlers
        #close window
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        #first toggle (Study temp) - best response speed vs actual value performance. In future, add a current value light
        elif event == '-TOGGLE-GRAPHIC-':   # click toggle button
            graphic_off = not graphic_off
            toggle_heat_func()
            client.publish("heattoggle", "Off") if graphic_off else client.publish("heattoggle", "On")

        #quick response as no check for current value
        elif event == '-TOGGLE-GRAPHIC1-':   # click next toggle button
            graphic1_off = not graphic1_off
            window['-TOGGLE-GRAPHIC1-'].update(image_data=toggle_btn_off if graphic1_off else toggle_btn_on)

        #update graphic per current value
        if(graphic_off):
            window['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_off)
        elif(not graphic_off):
            window['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_on)

        #display a timeout on GUI when temp has not been recieved for 'timeout' seconds
        if(time.time() > timesinceupdate + timeout):
            tempcstat = True
            window['-TEMP-'].update("*Timeout*")
        Timer(10.0, toggle_heat_func())

        if event == '-REBOOT-':
            os.system("sudo reboot now")
        if event == '-CLOSE-':
            break



    window.close()
    client.publish("heattoggle", "Off")




if __name__ == '__main__':
    toggle_btn_off = b'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'
    toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAAGQAAAAoCAYAAAAIeF9DAAARfUlEQVRoge1bCZRVxZn+qure+/q91zuNNNKAtKC0LYhs3R1iZHSI64iQObNkMjJk1KiJyXjc0cQzZkRwGTPOmaAmxlGcmUQnbjEGUVGC2tggGDZFBTEN3ey9vvXeWzXnr7u893oBkjOBKKlDcW9X1a137//Vv9ZfbNmyZTjSwhiDEAKGYVSYpnmOZVkzTdM8zTTNU4UQxYyxMhpzHJYupVSvUmqr67pbbNteadv2a7Ztd2SzWTiOA9d1oZQ6LGWOCJAACMuyzisqKroqGo1eYFlWxDRN3c4512OCejwWInZQpZQEQMa27WXZbHZJKpVank6nFYFzOGAOCwgR2zTNplgs9m/FxcXTioqKEABxvBL/SAsRngCwbXtNOp3+zpSLJzf3ffS5Jc8X/G0cam7DMIqKioruLy4uvjoej7NIJBICcbDnIN78cBXW71qH7d3bsTvZjoRMwpE2wIirjg0RjlbRi1wBBjcR5zFUx4ajtrQWZ46YjC+Mm4Gq0ipNJ8MwiGbTTNN8a+PyTUsSicT1jXMa0oO95oAc4k80MhqNvlBWVjYpHo9rrqD2dZ+sw9I1j6Nl/2qoGCCiDMzgYBYD49BghGh8XlEJRA5d6Z8EVFZBORJuSgEJhYahTfj7afMweczkvMcUcct7iUTikvr6+ta+0xIWAwJimmZdLBZ7uby8fGQsFtMo7zq4C/e+cg9aupphlBngcQ5OIFAVXvXA6DPZ5wkUIr4rAenfEyDBvfTulaMgHQWVVHC6HTSUN+GGP78JNUNqvCmUIiXfmkwmz6urq3s/f/oBARFC1MTj8eaKigq6ajCW/eZXuKd5EbKlGRjlBngRAzO5xxG8z0v7AAyKw2cNH180wQEmV07B2dUzcWbVFIwqHY2ySJnu68p04dOuHVi/Zx3eaF2BtXvXQkFCOYDb48LqieDGxptxwaQLw2kdx9mZSCSa6urqdgZt/QDhnBfFYjECY1JxcbEWU4+8/jAe+/DHME8wYZSIkCMKgOgLwueFKRTAJMPsmjm4YvxVGFUyyvs2LbF8iRCIL7+dLjs6d+DhdUvw7LZnoBiJMQnnoIP5p1yOK//sG+H0JL56e3ub6uvrtU4hLEKlTvrBNM37iouLJwWc8ejKH+Oxjx+FVW1BlAgtosDzCJ4PxEAgfJa5RAEnWiNw39QHcPqQCfqltdXkSCSSCWTSaUgyYcn4IZegqAiaboJjVNloLDxnMf667qu47pVvY5e7E2aVicc+ehScMVw+80r9E4ZhEK3vA/At+BiEHGIYRmNJScnblZWVjPTGyxuW4Z9Xf0+DYZQKMLM/GP2AGOy+X+cfdyElPbVsKu6f/gNURCr0uyaTSXR2duqrOsTXEO3Ky8v1lQZ1JA/i2hevwbsH10K5gL3fxh1Nd+L8My7wcFdKJZPJGePGjWt+9dVXPcHDGGOWZT1YXFysTdu2g21Y3Hy3FlPEGQVgMNYfDNa35hpyDiM+E5Wo3VTRhIdm/AjlVrn2I3bv3o329nakUin9LZyR/mQFzjCtfMY50qkU2ne362dcx0V5tAI/mfMEmqq+qEkiKgwsfvtu7DqwCwHtI5HIA3RvWZYHiBDiy0VFRdrpIz/jnlcWwy7Nap1RIKYCwvJBwAhByBG/P1h/xBXA6Oho3DvtARgQsG0HbW3tSCZT4AQAzweDhyBQG3iwSD2Akqkk2tva4WQdGNzAgxf9O0Zbo8EFQzaWweLli0KuEkI0bNu2bRbRn/viisIhWom/t2N9aNqyPjpjUK5AHhfwvHb+2QKEKYbvT1iIGI/BcST27dsL13U8MBgPweB5HOFd6W+h+7kPEFXHdbBn7x44rouoGcXds+4FyzDwIo6Wjmas274u4BKi/TWEAeecVViWdWEkYsEwBJauecLzM6LeD/VV4H3VwoT4GVgw7nZsvPgDr17k1VtOuh315gQoV/lWCXDr2O9i44Uf6HrL6Nshs7k+Kj9r+LnuWzFzFWRKes8eraKAi4ddgtPK66GURGdXpw8GL6gBR/S9Emhhf95VShddHR06vjVh+ARcMma29llEXODJtY+HksQwBGFQwTkX51qWZZmmhY7eTryzvxk8xrWfEZq2g+iM2SfMxf+c8xS+Ov5r/aj2d/Vfw09nPY1LSudoR8nXYGH/nHFzUS8nQNoyN2fQTcrvgANlq6PHIS4wr3a+Jlw6nUY2kwFjwhNPeaAInzOED4B3ZXmgsQI9Q5yTzmaQTmf03P/YcCVUGtp1WL2nGQd7OnwJwwmDc7kQ4ktBsPDNraugogCPHMKCYjnOuKvh7sMu34VnL0K9mgDpFOCBmBXD9WfeCJlU2qop4EByetN57X/oCoZJpZNRUzQSUklPeXMGoQEQ+toXGOYT3yO8yOMUkQcU1zpDcKHnpLlHVYzE5KopmkukCaza+uvwswkLAuR00u4EyLq2dV5symT9uaMAGIYrx14VNm1u3YQrHr8ctYtH4eT7R+PKn16Bzbs2hf3fGH81ZMItEE9UGsY0YHblXMBWA0ZcjlalldJU+QVNMOlKuFLqlU2rmAt/pecTXARXGuMBE4BGY3QANtyW8MAjn4XmllLhi6PO0iEWbgJrW9eGlhphwTnnY4P9jO0d27yQiBjEys5rbhjeqK879u3AxUsvxBvdr8EabsIaYWEVW4mvvHYpNrdv1mOaxjRB9voxIL88t/ZZfXP9jBvg9rr6BY9ZkcDpJRM0sRzb8QnsrWweXj1OITA05wTcQhwkhC/GvH4CQfgACh8w4iLbsbXYmnjiRB1WodXwScf2vEXITua0yxdsMu1Ot4MZrD8gff6cEJ+ImBnT98RyIs5hVAkYFYY2CMiRNCoNvHdgvR4Ti8QwMXpGASBL1z+BfT37MLRkKG4bf4dW4seqkCitiY7UxCIuITHFfTACEcR9YueLKw2CyOkW4hjBcyB4QOXaaH7y9kdVjgZ8g6U92Z7zZTgvJ0BKg4akm/ydHeruTDd4lOtKYAY6hpsMWxKbw3G1JWMLAGECeHrTU/p+7sSvoJ5P7CfSjlqRCnEjpsGAvykXiqVAmefpDtGnzauij0Um+t0TaQiUkkiJJxGUQoponuOQUp7vbarfgyKlRaXa9xho97C+4vTwftuBjwq1Omd48KMHsK93n+ag6yffqEMLx6SQESHJiJDeShV9iRuII5EHggg5RlejcHzQJ/KAIVGmuZA4Rfr7KAqFHr9SqjvYC46J2BGt0o29G5C0PWTPn3CBP3nhg/RDM6pn6PtkJon1nev7+TLEUQ+sv1/fk4IfUznmGCHihdClv2C0qBKFYGjlzVjhqmf9uSGnW3JmsAZSeFYSgd6Z6PJ+VAExEQ3fgbDgfsaEbhgeG6FZqZ9DNgBIq3d628NDS4fi2Yt/gdkVcz02lApfKpuJn037X4wuPUmP2di60RNnffZOiLNe6HwOm/d6oo1M4WNSGNCa+K1nBSnlE1uEK531UeqBWat1hfBM2wAAFoq6PCNAr36hudBVEjv2f+J9pVSojg7PTw7p5FLKj4NMiNqyWij7EB5y0MyARz58KGyuP7EeC2cuwqa/2Ko97f9oWoLThtSH/YtXLNKbWgX6KdhGEMB/fbT02AARFM6wqWOj9tBdx4Eg38E3ebnvhwiWrz9EKNY8P0XkiTkRWmnM7w84xXFtSFdhQ+t7Hi2kwpiK2vA1lFLbSGRtIkBIrk0bNU3vCWsPWYajCkS/R0iFjakNWLDilsN+681P3YgNqfUQxQIQhX3eljTDCx3PoaX1nf59R6lSWX2wWfsfru8vhA5eYLaKfEXPwvAJ83WDNnEDMISvX4QIn9W6Qy98ibe2v6mlA+WDTB05NeQQKeVm4pBfU74QPXDWqWeBpQCZUWFWRSEQuS1NmvC5jmfxV8/8JZ58p/8KX7rqCcx9ZA5+3vY0jAqh9+ALOSRHbZrrX7fQPs0xQoQpbOrdgJ09rZoOyXRa6wvB8j10plc744Gz6HEN90MnIvTchecMEucwFoou7alLhU/3/xbv7f6N53DbDGefdnb4yVLKlez111+vKCkp2V1VVWXRtu21//1NtDirYZ5ggFs8t6oHimfBQ1mlXLgJ6QUEHS/+pL3cGIco5uAxoc1g6nO6XDhdju43hxge5zAvOYD2n50OFzIrdTv1kzn9By86VCMxK/ZlXFd/k/60srIyUDg897GqMN4WEkLljcj/P9eazqTR1ekp8oW//Be8tONFzTXTKxvx0PyHPQtXqWxvb281iSxKd3wpk8lodp3f+HVNMEmiS+ZFYwfJtiP3nxPxqgxY1SYiNRYiIyzttZtDDW/r1/T0Byl2USpgDaM+s4DYBBCNNYeZ+nkCQ4f/j0bx3+2VjuXYevB9zSVdXV36Gsas8i0nFlhcOasrNy4/5sW8uTq9ubbs2oKXPvylTpuSWRfzm+aH7oLruoRBh6aIbdsPEUvZto3JtVPQVDlDp7BQrlGQ5hJi0kd0wVfMRDweF7rS6qbwMnGYDuHniTwCh/pELC9Eo/JA0Vwl9J6BflbhqFT9LiZwz/t3I5FN6D2MvXv3Qfoh+HxdEYixcKcw3BPxrClPZHGd00tz0DWZSeDOl+4AIl4q0PQTGjH91Aafrjpf64eEAfdl1/JMJkPpjhrJW8+/DVZXBE6P6+1ZBKD4Cl7JAYBRuT9C8SyPDjH/XyotCJOhTe3CXevvhO1k4Dg2drfv0fvoHkegQKfkgocMHPkhFYZUKqm3cWmOrGvju8/fhtZUq168RXYRFlx0e5gFKqVsqampeYWkFPcRUplM5ju9vb10RU1VDRacdTvsvbYX+LMLQQktr4FACcaE4AT16Orp36eS+YsIx7r0u7ij5XtIZpOwaddvzx60tbUhlUoXcgXru63LtPJub2vTz5AKIKd4wTM3oWVPi97WIF1188xbcVL1SQF3UBL2dXRPtBfz5s0LOnYqpYYahjGd9kfqauqgeoCWT1v0ytHZibxvdiILdV2/GNihPP6jpBp+5xJs5XKgLdWGVTtWYnxxHYZEh2ix09Pdg67uLmRtG45taxFPFiqB0NXdjb1796K7u0uPpbK1/QPc9PwN+KDrfe2HkfX69UlX4LKZ8zR30EKl7PgRI0Y8TOMvu+yyXF6W33ljT0/PDMoXIna8etY1Or71oy0PDZwo5yt6FQDTxwIbFJRjGGk/XNGvbnBQFIkSyP9pzbdwbsUs/E3d32J46QhIx0F3VxfCXCDi/mBF6sWp0Na1E0+2PImXt70MFkHIGQTGtRd8W4MBL3uR8nxvCF6JMGArVqwoeEXDMMJUUjKDKWHuxXd/gbtWfR92Wdbbbz8OUkmVn6erUtIz6RMSddHTMH1YI+qH1uPE0hEoiRRrEHqyPWjrbMPm3ZvQ/Onb2LhvE5ihNI3IUo3YEdwycwFmN1yaD8ZOylqsra0NU0kJi36AwE+2jsfjOtk6yGJs3d+KRS8vRPOBt3LJ1hGWE2efx2RrnVztRS5kxvOzdE1LL9ud+tzCkJK3SJneoyfTtnFYE26+cAHGVI/RRkCQbJ1IJM6rra0tSLYeFJDgOEIsFguPI9A2L7Wv+XgN/vOdn6B591tAnB0fxxECYBy/ZqUHhJsLo8Pf3yBHGRmgYUQT/qFxPhrHN2ogkFMLJKYuHTt27Kd9f4awGPDAjm8XE4pNUsr7HccJD+xMPXkqpo2dhgM9B7Dy/TfwbutabOvchvYD7eh1e+HS3uTn+cCO9I+vSe+ew0CxiKM6Xo3ailpMrpmiwyHDKqpDp88/SUXW1JLe3t7rx48fP/iBnYE4JL8QupZl0ZG2H8Tj8emUs/qnI21HVvKOtLUkk8nrxo0b9/ahHhyUQ/ILOYqZTKbZcZyGTCYzK5lMfjMajZ4fiUT0oU8vIir+dOgz79CnHz3P2rb9q0wm88NTTjll+ZHOc1gOKRjsn8Y1TZOORVOC3dmWZdUbhqGPRXPOS49TQHqUUj1SSjoWvdlxnJXZbPa1bDbbQb4K1SM6Fg3g/wC58vyvEBd3YwAAAABJRU5ErkJggg=='
    Abort = b'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'
    Bomb = b'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'


    main()















