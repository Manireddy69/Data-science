#!/usr/bin/env python
# coding: utf-8

# In[112]:


import numpy as np
x = np.random.random((3,3))
y = np.random.normal(2,3,(2,2))#takes as mean = 2 & std = 3 & create a (2,2) matrix
print(x)
print(x.dtype)


# In[90]:


x = np.random.random((4,4))
abs(x)


# In[122]:


c = np.random.randint(1,5,(2,2))
v = np.random.randint(1,5,(2,2))
conc = np.concatenate([c,v]) #one way to combine two array
vst = np.vstack([c,v])# this is also combine two array but in vertical way
hst = np.hstack([c,v])#this is for horizontal array
print(conc)
print(vst)
print(hst)


# In[131]:


x = np.arange(6) # works as range(6)
x.reshape(3,2) # it concert int matrix but we should correct number of elements


# In[156]:


n = [2,3,6]
print(n)
print("2^x :",np.power(2,n))
print("e^x :",np.exp(n))


# ## Eigenvalues & Eigenvectors

# In[167]:


e = np.random.randint(1,5,(2,2))
eigenvalues,eigenvectrs = np.linalg.eig(e) #eig returns both eigenvalues and eigenvectors
print("the matrix is:\n",e)
print("The eigen values are:\n",eigenvalues)
print("The eigen vectors are:\n",eigenvectors)


# # Determinant of matrix

# In[169]:


np.linalg.det(e) #gives the determinant of matrix


# In[172]:


i = np.random.rand(190)
get_ipython().run_line_magic('timeit', 'sum(i)')
get_ipython().run_line_magic('timeit', 'np.sum(i)')

