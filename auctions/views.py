from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, id):
    listingData=Listing.objects.get(pk=id)
    isListingInWatchlist=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
       
            
    })


def closeAuction(request, id):
    listingData=Listing.objects.get(pk=id)
    listingData.isActive=False
    isListingInWatchlist=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    listingData.save()
    return render(request, "auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "updated": True,
        "message":  "congrats! the Auction is closed"
    })

def addBid(request, id):
    newBid=request.POST["newBid"]
    listingData=Listing.objects.get(pk=id)
    isListingInWatchlist=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData) 
 
    if int(newBid) > listingData.price.bid:
        updatedBid=Bid(user=request.user, bid=int(newBid))
        updatedBid.save()
        listingData.price=updatedBid
        listingData.save()
        return render(request, "auctions/listing.html",{
            "listing": listingData,
            "message":  "Bid was updated successfully",
            "updated": True,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            
         })
    else:
        return render(request, "auctions/listing.html",{
            "listing": listingData,
            "message":  "Bid updated Failed.",
            "updated": False,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            
        })
    
    
def addComment(request, id):
    currentUser=request.user
    listingData=Listing.objects.get(pk=id)
    message=request.POST['newComment']
    
    newComment=Comment(
        author=currentUser,
        listing=listingData,
        message=message

    )
    newComment.save() #save the new comment in database
    return HttpResponseRedirect(reverse("listing",args=(id, )))


def displayWatchlist(request):
    currentUser=request.user
    listings =currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })


def addWatchlist(request, id):
    listingData=Listing.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))



def removeWatchlist(request, id):
    listingData=Listing.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))




def index(request):
    activeListings=Listing.objects.filter(isActive=True)
    all_categories= Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings": activeListings,
        "categories": all_categories 
    })

def displayCategory(request):
    category_data= None
    if request.method=="POST":
        categoryFromForm=request.POST['Category']
        if categoryFromForm:
            category_data=Category.objects.get(category_name=categoryFromForm)
            activeListings=Listing.objects.filter(isActive=True, category=category_data)
        else:
            activeListings=Listing.objects.filter(isActive=True)
        all_categories= Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings": activeListings,
            "categories": all_categories 
        })
    return render(request,"auctions/displayCategory.html")
    
   
  


def CreateListing(request):
    if request.method == "GET":
        all_categories= Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories":all_categories

        })
    else:

        #get the data from the form 
        title=request.POST["title"]
        description=request.POST["description"]
        imageurl=request.POST["imageurl"]
        price=request.POST["price"]
        category_name=request.POST["Category"]
        #who is the user 
        current_user= request.user
        #get all content about the category
        try:
            category_data=Category.objects.get(category_name=category_name)
        except Category.DoesNotExist:
            #handle the case when the category does not exist
            return render(request,"auctions/create.html",{
                "categories":Category.objects.all(),
                "error_message":"invalid category."
            })
        # create object of bid:
        bid=Bid(bid=float(price), user=current_user)
        bid.save()
        #create a new listing object
        new_Listing=Listing(

            title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,
            category=category_data,
            owner=current_user
        )
        #insert the object in the database
        new_Listing.save()
        #redircect to index page
        return HttpResponseRedirect(reverse(index))
    

  



