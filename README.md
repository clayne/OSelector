PS: If you want a better looking version, visit this **[LINK](https://hyperen0r.github.io/OSelector/)**

# OSelector

**OSelector** is a tool to generate a poser plugin for **OSA**. You can easily generate
a plugin for any mod you have installed, allowing you to test every animation using **FNIS**
through **OSA UI**. The plugin is an xml file using the *MyAnimation* functionality. So no
esp slot taken.

Description of MyAnimation from **OSA**:  

> MyANIMATION: functions exactly the same as MyEquip except it plays animations. 
> It's a text data poser mod without the need for rings. You can group your animations into categories however you like. 
> They can play directly from the list on the player character or on a target. Note that MyAnim is different from the animation engine, 
> the animation engine has lots of empowered features for animated scene creators where as MyAnim functions like a poser mode
> where it simply plays single animations.  
[Nexus Link](https://www.nexusmods.com/skyrim/mods/76744/?tab=description&topic_id=5756447)

### With just a click :
![Tool Overview](ressources/tool_overview.png)



## How does it works ?

There is three major step :

* First step is to scan the folder of your choice *(usually data/ or mods/)*.
It will register every animation using **FNIS**

* During second step, a tree structure will be displayed. It represents the navigation menu
you will see in game. You can make some edit to it, change name and modify the organization.
To prevent the screen from being cluttered with entries, each page is limited to 25 items (configurable)
at generation. It means that the tool will organize the tree in such a way that no more
than 25 items are displayed. But if you edit it yourself, this rule is not applied
(Meaning you can force a page to have more than 25 entries). 

* The third and final step is the plugin generation, where you specify the
name of your plugin.

If you use Mod Organizer, the plugin should be installed in your mods folder. Then you just have to
activate it in Mod Organizer.

You can also load existing plugin and tweak it.



## Usage In-Game

To use the plugin, you must have **OSA** installed. Then press **Enter** on your numpad to
open **OSA UI**. Then go to __Inspect Self > Interact > Animate > [NAME OF YOUR PLUGIN]__. Depending of the
number of animations and your PC, it can take some time to load the plugin.


## For who is this tool ?

Anyone who want to make an easy navigation menu for a mod containing animations
or for his entire data folder.

Anyone who want to make a navigation menu with better names and organization or to tweak an 
existing one

* Mod Users can just launch the tool to have a menu for every or some animations. Everyone 
can share his file, if he did some edit (better names and organization, like Morra's Poser Pack).

* Mod Author can add this file to their mod, so when a user has OSA and his mods, he can easily
cycle through his animations. 

## How many animations ?

The tool should be able to handle a very large amount of animations. Each mod have usually one
**FNIS** file, containing information about animations. Some have more than one **FNIS** file.
However if one file contains more than 8 750 animations (It's a lot, the most I have seen
is ~2 750 from Halo's mod), I cannot guarantee anything.

I've tested with roughly 14 000 animations and everything seemed fine.



## Animation supported
  Normally all animations using FNIS should work out of the box. (The xml file is just
  exposing animation id to OSA engine)
  
  I could test only the following :
  
* Basic animation (Pose)
* Sequence animation (Animation with multiple stages) 
* AnimObj animation (Animation with objects)



## Configurations

Some settings (like the max number of items per page) can be changed by editing
the conf.ini file. If you do not see one, launch the tool once.
It will automatically generate a new one.



##Tools used

* IDE : [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/#section=windows)
* Python : 3.6 (PyInstaller does not support 3.7 for now)
* Libraries : PyQt (for the GUI) and PyInstaller (for the executable)



## FAQ

##### Q: There is bug ! / I have some ideas for improving/fixing the tool
**A** If you want to report an issue or feature request, feel free to open a ticket through github.
To do so, go to **[ISSUES](https://github.com/Hyperen0r/OSelector/issues)**, click on _**New Issue**_
and chose one of the templates. 

##### Q: Why some names are so weird ?
**A:** The Tool is supposed to handle all kind of animations using FNIS. But not every modder follow
the same naming guidelines. So the tool is dependant of the three following names:

* Package name (name of the mod)
* Module name (name of the FNIS file, for example for "FNIS_3ijou_List.txt", it will be "3ijou" )
* Animation name (More exactly name of the stage, like "EXT16")

There is some tweak applied to each of them to be more readable and understandable,
but this a functionality I want to improve.

Also, some names are very long which overlap with other entries from OSA UI. To prevent this,
each string is limited to 25 characters (also configurable)

And last thing, the tree is automatically cleaned up of every folder containing zero child,
or only one child (the child replace his parent). For now I haven't found a way to guess
which name is better (the child or the parent ?).

##### Q: I'm afraid to use an executable/ My anti-virus blocked your file
**A:** I had no problem with my antivirus (Avira), and the exe was clean on Virus Total. 
If you are suspicious, you can do the following:

* Check with **[Virus Total](https://www.virustotal.com/#/home/upload)**
* Check the source. **[Github link](https://github.com/Hyperen0r/OSelector)**
* Execute directly from source. In that case, please refer to **[Tools Used](##Tools-Used)**
to help you setup your environment.

## Known Bug

 - [ ] Menu entry is duplicated. Sometimes after closing and reopening, all menu entries are
 duplicated (even the one not generated with the tool)

## Thanks

* Thanks to CE0 and the OSA Team for this awesome engine/framework