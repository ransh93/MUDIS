# MUDIS

### What is MUDIS and why should you use it?

MUDIS - MUD Inspection System is a tool that compares the network behavior of IOT devices, based on their formal description in the MUD file
MUDIS tool introduces comparison and generalization features, allowing users to investigate MUD files differences.

### So, what can it do (or what is MUDIS features)?
Motivated by the impact of location on the MUD, we built
this tool, which as few fundamental features:

<details><summary><b>ADD A NEW MUD<b></summary>
<p>

This is a basic feature that gives researchers the opption to add MUDS into the system.<br>
The uploaded MUD is them saved at the server and in a dedicated MongoDB for further use.<br>
When adding a new MUD you can add some helpful metadata like - device name, device type, the device geo location etc.

</p>
</details>
  
<details><summary><b>MUD parser<b></summary>
<p>

The basic concept of MUDIS is its parsing engine which gives MUDIS its power.<br>
The parsing engine knows how that take a raw MUD file and convert it into python objects that defines the given MUD.<br>
Once MUDIS proccess the MUD it creates - Matches objects, Aces objects, ACLs and so on.<br>
This objects above creates a MUD object that MUDIS will use in the more complex features it has.

</p>
</details>
  
<details><summary><b>COMPARE MUDS<b></summary>
<p>

Once you done uploading two or more MUDs you can start using one of the main feature of MUDIS, the comparison feature.<br>
This feature is using the MUD object that was created using the MUDIS parsing engine (explained in the previous section) to find the followin things:
* Identical ACEs - these are ACEs that exsists in both MUDs compared together.
* Domain based similarity ACEs - these are ACEs from both MUDs that has similar domains (More about similarity in our paper) with the ame port and protocol.
* Clustered ACEs - This ACEs are being paired based on their port+protocol similarity or by their IPs similarity of by domains similarity with a different port.
* Dissimilar ACEs - ACEs that has now given similarity with ACEs on the other MUD that we compared to.

In addition, the comparison results in a similarity score that the researcher can use to asstimaate how identical are the two MUDs.<br>
This is an importent metric that we used during our research (moreover inside our paper)

To conclude, MUD comparison allows the research to calculates the MUD similarity measure and then examine the differences between two MUD
files and highlight similar entries. This allows us to drill down and gain insights about the origin of the differences.
  
</p>
</details>

#### Add a new MUD
This is a basic feature that gives researchers the opption to add MUDS into the system.<br>
The uploaded MUD is them saved at the server and in a dedicated MongoDB for further use.<br>
When adding a new MUD you can add some helpful metadata like - device name, device type, the device geo location etc.

#### Add a new MUD


which gets two MUDs as input and performs
two tasks:

* MUD Comparison - calculates the MUD similarity measure. It then examines the differences between two MUD
files and highlights similar entries. This allows us to drill
down and gain insights about the origin of the differences.
* MUD Generalization - creates a generalized MUD that
can serve as a white-list for the network behavior of both
MUDs (represent two locations in our experiments), this
is done by covering both input MUDs.
