from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.fields.related import ManyToManyField
from .forms import SelectFoodForm,AddFoodForm,CreateUserForm,ProfileForm
from .models import *
from datetime import timedelta
from django.utils import timezone
from datetime import date
from datetime import datetime
from .filters import FoodFilter
from django.forms.models import model_to_dict



#home page view
@login_required(login_url='login')
def HomePageView(request):

	#taking the latest profile object
	calories = Profile.objects.filter(person_of=request.user).last()
	calorie_goal = calories.calorie_goal
	height = calories.height
	weight = calories.weight
	sex = calories.sex
	age = calories.age
	bmi = calories.bmi
	bmr = calories.bmr
	tdee = calories.tdee
	exercise_level = calories.exercise_level
	
	#creating one profile each day
	if date.today() > calories.date:
		profile=Profile.objects.create(person_of=request.user)
		profile.save()

	calories = Profile.objects.filter(person_of=request.user).last()
		
	# showing all food consumed present day

	all_food_today=PostFood.objects.filter(profile=calories)
	
	calorie_goal_status = calorie_goal -calories.total_calorie
	over_calorie = 0
	if calorie_goal_status < 0 :
		over_calorie = abs(calorie_goal_status)

	# BMI check
	# if bmi != 0:
	bmi = round(weight / (height/100)**2, 1)
	
	if bmi < 18.5:
		bmi_class = 'Underweight'
	elif bmi >= 18.5 and bmi <= 24.9:
		bmi_class = 'Normal Weight'
	elif bmi >= 25 and bmi <= 29.9:
		bmi_class = 'Overweight'
	elif bmi >= 30 and bmi <= 34.9:
		bmi_class = 'Obesity'
	elif bmi >= 35:
		bmi_class = 'Severe obesity'

	# BMR
	s = 0
	if sex == 'male':
		s = 5
	elif sex == "female":
		s = -161

	bmr = 10 * weight + 6.25 * height - 5 * age + s

	# Total Daily Energy expenditure
	if exercise_level == 'sedentary':
		tdee = bmr * 1.2
	elif exercise_level == 'light':
		tdee = bmr * 1.375
	elif exercise_level == 'moderate':
		tdee = bmr * 1.55
	elif exercise_level == 'very':
		tdee = bmr * 1.725
	elif exercise_level == 'extra':
		tdee = bmr * 1.9

	# Sedentary (little or no exercise) : Calorie-Calculation = BMR x 1.2

	# Lightly active (light exercise/sports 1-3 days/week) : Calorie-Calculation = BMR x 1.375

	# Moderately active (moderate exercise/sports 3-5 days/week) : Calorie-Calculation = BMR x 1.55

	# Very active (hard exercise/sports 6-7 days a week) : Calorie-Calculation = BMR x 1.725

	# If you are extra active (very hard exercise/sports & a physical job) : Calorie-Calculation = BMR x 1.9

	
	context = {
	'total_calorie':calories.total_calorie,
	'calorie_goal':calorie_goal,
	'calorie_goal_status':calorie_goal_status,
	'over_calorie' : over_calorie,
	'food_selected_today': all_food_today,
	'height': height,
	'weight': weight,
	'bmi': bmi,
	'bmi_class': bmi_class,
	'bmr': bmr,
	'tdee' : tdee,
	'exercise_level': exercise_level
	}
	

	return render(request, 'home.html',context)

#signup page
def RegisterPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request,"Account was created for "+ user)
				return redirect('login')

		context = {'form':form}
		return render(request,'register.html',context)

#login page
def LoginPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:

		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(request,username=username,password=password)
			if user is not None:
				login(request,user)
				return redirect('home')
			else:
				messages.info(request,'Username or password is incorrect')
		context = {}
		return render(request,'login.html',context)

#logout page
def LogOutPage(request):
	logout(request)
	return redirect('login')

#for selecting food each day
@login_required
def select_food(request):
	person = Profile.objects.filter(person_of=request.user).last()
	#for showing all food items available
	food_items = Food.objects.filter(person_of=request.user)
	form = SelectFoodForm(request.user,instance=person)

	if request.method == 'POST':
		form = SelectFoodForm(request.user,request.POST,instance=person)
		if form.is_valid():
			
			form.save()
			return redirect('home')
	else:
		form = SelectFoodForm(request.user)

	context = {'form':form,'food_items':food_items}
	return render(request, 'select_food.html',context)

#for adding new food
def add_food(request):
	#for showing all food items available
	food_items = Food.objects.all()
	form = AddFoodForm(request.POST) 
	if request.method == 'POST':
		form = AddFoodForm(request.POST)
		if form.is_valid():
			profile = form.save(commit=False)
			profile.person_of = request.user
			profile.save()
			return redirect('add_food')
	else:
		form = AddFoodForm()
	#for filtering food
	myFilter = FoodFilter(request.GET,queryset=food_items)
	food_items = myFilter.qs

	# f_dict = to_dict()
	# f_dict = model_to_dict(Food(), fields=[field.name for field in food_items._meta.fields])
	f_dict = list(Food.objects.values())

	c = request.GET
	if not c:
		s=0
	else:
		a = c['food_name'][0]
		mergeSort(f_dict)
		s = binarySearch(f_dict, 0, len(f_dict)-1, a)
	
	

	context = {'form':form,'food_items':food_items,'myFilter':myFilter, 'fd': f_dict, 's': s,'c': c}
	return render(request,'add_food.html',context)

#for updating food given by the user
@login_required
def update_food(request,pk):
	food_items = Food.objects.filter(person_of=request.user)

	food_item = Food.objects.get(id=pk)
	form =  AddFoodForm(instance=food_item)
	if request.method == 'POST':
		form = AddFoodForm(request.POST,instance=food_item)
		if form.is_valid():
			form.save()
			return redirect('profile')
	myFilter = FoodFilter(request.GET,queryset=food_items)

	
	context = {'form':form,'food_items':food_items,'myFilter':myFilter}

	return render(request,'add_food.html',context)

#for deleting food given by the user
@login_required
def delete_food(request,pk):
	food_item = Food.objects.get(id=pk)
	if request.method == "POST":
		food_item.delete()
		return redirect('profile')
	context = {'food':food_item,}
	return render(request,'delete_food.html',context)

#profile page of user
@login_required
def ProfilePage(request):
	#getting the lastest profile object for the user
	person = Profile.objects.filter(person_of=request.user).last()
	food_items = Food.objects.filter(person_of=request.user)
	form = ProfileForm(instance=person)

	if request.method == 'POST':
		form = ProfileForm(request.POST,instance=person)
		if form.is_valid():	
			form.save()
			return redirect('profile')
	else:
		form = ProfileForm(instance=person)

	#querying all records for the last seven days 
	some_day_last_week = timezone.now().date() -timedelta(days=7)
	records=Profile.objects.filter(date__gte=some_day_last_week,date__lt=timezone.now().date(),person_of=request.user)

	context = {'form':form,'food_items':food_items,'records':records}
	return render(request, 'profile.html',context)



	# chat_messages.objects.all().values_list('name')
def to_dict(instance):
	# def to_dict(self, instance):
	opts = instance._meta
	data = {}
	for f in opts.concrete_fields + opts.many_to_many:
		if isinstance(f, ManyToManyField):
			if instance.pk is None:
				data[f.name] = []
			else:
				data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
		else:
			data[f.name] = f.value_from_object(instance)
	return data
	

def mergeSort(arr):
    if len(arr) > 1:
 
         # Finding the mid of the array
        mid = len(arr)//2
 
        # Dividing the array elements
        L = arr[:mid]
 
        # into 2 halves
        R = arr[mid:]
 
        # Sorting the first half
        mergeSort(L)
 
        # Sorting the second half
        mergeSort(R)
 
        i = j = k = 0
 
        # Copy data to temp arrays L[] and R[]
        while i < len(L) and j < len(R):
            if L[i]['name'] < R[j]['name']:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
 
        # Checking if any element was left
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
 
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1
# print(list(a))
# print(a[1]['name'])


def binarySearch(arr, l, r, x): 
  
    while l <= r: 
  
        mid = l + (r - l) // 2; 

        # Check if x is present at mid
        if arr[mid]['name'] == x: 
            return arr[mid]
  
        # If x is greater, ignore left half 
        elif arr[mid]['name'] < x: 
            l = mid + 1
  
        # If x is smaller, ignore right half 
        else: 
            r = mid - 1
      
    # If we reach here, then the element 
    # was not present 
    return -1
