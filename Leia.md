# Referências e Documentação: Arduino & Pyfirmata2

Este documento reúne os links essenciais para o desenvolvimento com Arduino Uno, configuração de ambiente e integração com Python via Pyfirmata2.

## 1. Hardware: Arduino Uno Rev3
Documentação técnica oficial sobre a placa, incluindo esquemáticos, pinagem (pinout) e especificações de energia.
* **Link:** [Arduino Uno Rev3 Hardware Docs](https://docs.arduino.cc/hardware/uno-rev3/)

## 2. Software: Arduino IDE
Link para download e guias de uso da Interface de Desenvolvimento Integrada (IDE) oficial, necessária para carregar o protocolo *StandardFirmata* na placa.
* **Link:** [Arduino IDE Software Docs](https://docs.arduino.cc/software/ide/)

## 3. Drivers Seriais
Para que o computador reconheça a placa Arduino via USB, é necessário ter os drivers instalados. Placas oficiais usam os drivers da própria IDE, enquanto placas compatíveis (clones) geralmente utilizam o chip CH340.
* **Guia de Instalação de Drivers (Oficial):** [Arduino Driver Installation](https://docs.arduino.cc/software/ide-v1/tutorials/driver-installation)
* **Drivers CH340 (Placas Compatíveis):** [SparkFun CH340 Guide](https://learn.sparkfun.com/tutorials/how-to-install-ch340-drivers/all)

## 4. Integração Python: Pyfirmata2
Documentação oficial da biblioteca utilizada para controlar o Arduino em tempo real usando Python. Contém exemplos de callbacks e controle de amostragem.
* **Link Oficial (PyPI):** [pyfirmata2 Documentation](https://pypi.org/project/pyfirmata2/)
* **Repositório GitHub:** [pyfirmata2 GitHub](https://github.com/p-bernd/pyfirmata2)

---
*Documento gerado para auxiliar no projeto de automação com Python.*