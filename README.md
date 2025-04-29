# COSC364 | Implementation of RIPv2 Protocol in Python

## About
This is an implementation of the RIPv2 protocol in Python. It was programmed for assignment one of COSC364 by:
- Max Moir (mmo199)
- Martyn Gascoigne (mga138)

It implements the basic RIP routing protocol with Split Horizon and Poison Reverse. The corresponding report for this assignment can be found [here](https://docs.google.com/document/d/10RFQYFbunvFVc-qG-XOu6w017vL2BolW4NwpVfRP8Wg/edit?tab=t.0#heading=h.8vi7o980eq7y)

## Configuration
The program is designed to converge upon an ideal network state from a given set of router config files. Config files bust be written in the following format:
```text
    router-id [id]
    input-ports [port-number], [port-number], …
    output-ports [port-number]-[metric-value]-[peer-router-id], …
```

Example config files are located in `src/cfgs`.

## How to run
First, clone the project using the following command:
```bash
    $ git clone https://github.com/maxwmoir/rip-project.git
```
After this enter the project repository and create a virtual enviroment.

```bash
    $ cd rip-project

    $ python -m venv venv 
```
After activating your enviroment the program can be run from the command line by supplying the name of the config file.

```bash
    $ python -m daemon.py "path-to-config" 
```

## Todo
- [x] Make sure all methods have docstring
- [ ] Fix Operation not permitted error with sock.send
- [x] Remove unnecessary prints and commenting
- [ ] Reorder methods
- [x] Remove use of magic nos.
