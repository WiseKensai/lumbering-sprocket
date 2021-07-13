#!/usr/bin/python3

def edit_me():
  """ You can set up an arbitrary number of HGB dice experiments here.
      I've set up two, so you can see how it's done.
      Available traits:
        * agile      : True/False
        * precise    : True/False
        * advanced   : True/False
        * infantry   : True/False
        * field_armor: True/False
        * ap         : #
        * dot        : # (use this for fire, set to 1 for haywire or corrosion)
        *
  """
  traits1 = {'precise': True,
             'ap': 1}
  exp1 = HGB_Dice_Experiment(2,4, # Attacker Dice, Attacker Skill
                             2,4, # Defender Dice, Defender Skill
                             6,6, # Weapon Damage, Defender AR
                             4,2, # Defender H,S
                             traits1)

  traits2 = {'agile': True}
  exp2 = HGB_Dice_Experiment(2,4, # Attacker Dice, Attacker Skill
                             2,4, # Defender Dice, Defender Skill
                             6,6, # Weapon Damage, Defender AR
                             4,2, # Defender H,S
                             traits2)

  compare_experiments([exp1,exp2])

# Here be dragons. Edit what follows at your own risk!
"""""""""""""""""""""""""""""""""""""""""""""""""""
@@@@@@@@@@@@@@@@@@@@@**^^""~~~"^@@^*@*@@**@@@@@@@@@
@@@@@@@@@@@@@*^^'"~   , - ' '; ,@@b. '  -e@@@@@@@@@
@@@@@@@@*^"~      . '     . ' ,@@@@(  e@*@@@@@@@@@@
@@@@@^~         .       .   ' @@@@@@, ~^@@@@@@@@@@@
@@@~ ,e**@@*e,  ,e**e, .    ' '@@@@@@e,  "*@@@@@'^@
@',e@@@@@@@@@@ e@@@@@@       ' '*@@@@@@    @@@'   0
@@@@@@@@@@@@@@@@@@@@@',e,     ;  ~^*^'    ;^~   ' 0
@@@@@@@@@@@@@@@^""^@@e@@@   .'           ,'   .'  @
@@@@@@@@@@@@@@'    '@@@@@ '         ,  ,e'  .    ;@
@@@@@@@@@@@@@' ,&&,  ^@*'     ,  .  i^"@e, ,e@e  @@
@@@@@@@@@@@@' ,@@@@,          ;  ,& !,,@@@e@@@@ e@@
@@@@@,~*@@*' ,@@@@@@e,   ',   e^~^@,   ~'@@@@@@,@@@
@@@@@@, ~" ,e@@@@@@@@@*e*@*  ,@e  @@""@e,,@@@@@@@@@
@@@@@@@@ee@@@@@@@@@@@@@@@" ,e@' ,e@' e@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@" ,@" ,e@@e,,@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@~ ,@@@,,0@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@,,@@@@@@@@@@@@@@@@@@@@@@@@@
"""""""""""""""""""""""""""""""""""""""""""""""""""
# https://textart.io/art/tag/dragon/1

import copy,collections,random

class HGB_Dice_Experiment:
  def __init__(self,
               diceA,skillA,
               diceB,skillB,
               dam,ar,
               hull,structure,
               traits,
               nsamples=10000,
               target_damage=2):
    self.diceA = diceA
    self.skillA = skillA
    self.diceB = diceB
    self.skillB = skillB
    self.dam = dam
    self.ar = ar
    self.hull = hull
    self.structure = structure
    self.traits = traits
    self.nsamples = nsamples
    self.target_damage = target_damage

    self.samples = self.monte_carlo_mos()
    self.damage = self.process_damage()
    self.damage_hist = collections.Counter(self.damage)

  def roll_dice(self,dice,skill):
    rolls = [random.randrange(1,7) for i in range(dice)]
    base = max(rolls)
    rolls.remove(base)
    return base + sum([1 if i >= skill else 0 for i in rolls])


  def monte_carlo_mos(self):
    bonus = 0;
    if 'precise' in self.traits and self.traits['precise']:
      bonus = bonus + 1
    if 'advanced' in self.traits and self.traits['advanced']:
      bonus = bonus + 1
    return [self.roll_dice(self.diceA,self.skillA) -
            self.roll_dice(self.diceB,self.skillB) +
            bonus for i in range(self.nsamples)]

  def process_damage(self):
    damage = copy.copy(self.samples)

    agile       = False if "agile" not in self.traits else self.traits["agile"]
    infantry    = False if "infantry" not in self.traits else self.traits["infantry"]
    field_armor = False if "field_armor" not in self.traits else self.traits["field_armor"]
    ap          = 0 if "ap" not in self.traits else self.traits["ap"]
    dot         = 0 if "dot" not in self.traits else self.traits["dot"]

    for i in range(len(self.samples)):
      if self.samples[i] < 0:
        damage[i] = 0
      elif self.samples[i] == 0 and agile:
        damage[i] = 0
      else:
        cal = max(0,self.samples[i] + self.dam - self.ar);
        if ap > 0:
          damage[i] = max(cal,max(1,min(ap,self.samples[i])))
        else:
          if cal == 0:
            damage[i] = random.randint(0,1)
          else:
            damage[i] = cal

        if infantry:
          damage[i] = max(2,damage[i])
        if field_armor and damage[i] > 0:
          damage[i] = max(1,damage[i]-1)
        for f in range(dot):
          damage[i] = damage[i] + random.randint(0,1)
    return damage

  def calculate_hit(self):
      histogram = collections.Counter(self.samples)
      hit = 0
      agile = False if "agile" not in self.traits else self.traits["agile"]
      for i in range(min(self.samples),max(self.samples)+1):
        chance = histogram[i]*100.0/len(self.samples)
        if i == 0 and not agile:
          hit = hit + chance
        elif i < 0:
          hit = hit + chance

      return hit

  def calculate_takeaways(self):
    histogram = self.damage_hist
    agile = False if "agile" not in self.traits else self.traits["agile"]
    target = 0
    cripple = 0
    kill = 0
    for i in range(min(self.damage),max(self.damage)+1):
      chance = histogram[i]*100.0/len(self.damage)
      if i >= self.target_damage:
        target = target + chance
      if i >= self.hull:
        cripple = cripple + chance
      if i >= self.hull+self.structure:
        kill = kill + chance
    return target,cripple,kill

  def __str__(self):
    histogram = collections.Counter(self.samples)
    print("Mean MoS: {0:3.2f}".format(sum(self.samples)*1.0/len(self.samples)))
    print("MoS: % chance")
    for i in range(min(self.samples),max(self.samples)+1):
      print("  {0:2d}: {1:6.3f}".format(i,histogram[i]*100.0/len(self.samples)))

    print("Mean Damage: {0:3.2f}".format(sum(self.samples)*1.0/len(self.samples)))
    print("Damage: % chance")
    for i in range(min(self.samples),max(self.samples)+1):
      print("  {0:2d}: {1:6.3f}".format(i,histogram[i]*100.0/len(self.samples)))


def compare_experiments(experiments):
    minimum = min([min(exp.damage) for exp in experiments])
    maximum = max([max(exp.damage) for exp in experiments])

    width = 15


    metadata_titles = ["Dice","Skill","Dam v AR","H/S"]
    metadata = []
    for exp in experiments:
      dice = "{0}d6 v {1}d6".format(exp.diceA,exp.diceB)
      skill = "{0}+ v {1:2d}+".format(exp.skillA,exp.skillB)
      damar = "{0:2d} v {1:3d}".format(exp.dam,exp.ar)
      hs = "{0}/{1}".format(exp.hull,exp.structure)
      metadata.append((dice,skill,damar,hs))
    for i in range(len(metadata_titles)):
      form = " {{0:>{0}}}".format(width)
      print(form.format(metadata_titles[i]),end="")
      for j in range(len(metadata)):
        print(form.format(metadata[j][i]),end="")
      print("")

    trait_titles = list(set().union(*[list(exp.traits.keys()) for exp in experiments]))
    traits = []
    for exp in experiments:
      exp_traits = []
      for title in trait_titles:
        exp_traits.append(" " if title not in exp.traits else exp.traits[title])
      traits.append(exp_traits)
    for i in range(len(trait_titles)):
      form = " {{0:>{0}}}".format(width)
      print(form.format(trait_titles[i]),end="")
      for j in range(len(traits)):
        print(form.format(traits[j][i]),end="")
      print("")


    for i in range(minimum,maximum+1):
      form = " {{0:{0}d}}".format(width)
      print(form.format(i),end="")
      for exp in experiments:
        val = 0 if i not in exp.damage_hist else exp.damage_hist[i]*100.0/len(exp.damage)
        form = " {{0:{0}.3f}}".format(width)
        print(form.format(val),end="")
      print("")

    takeaways = []
    for exp in experiments:
      hit = exp.calculate_hit()
      target,cripple,kill = exp.calculate_takeaways()
      takeaways.append((hit,target,cripple,kill))

    takeaway_titles=["Hit",">={0}".format(experiments[0].target_damage),"Cripple","Kill"]

    for i in range(len(takeaway_titles)):
      form = " {{0:>{0}}}".format(width)
      print(form.format(takeaway_titles[i]),end="")
      form = " {{0:{0}.3f}}".format(width)
      for j in range(len(takeaways)):
        print(form.format(takeaways[j][i]),end="")
      print("")


if __name__ == "__main__":
    random.seed(42)
    edit_me()
