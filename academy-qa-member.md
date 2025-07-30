# Onboarding Flow for QA Member role Users

Template: 
1. Decisions and notes while drafting the learning path will be marked as quote blocks with a > at the beginning of the line.
2. The Stages in the user journey should be marked with a ## (double hash) at the beginning of the line. They will be heading two.
3. Each asset will be in heading 4 with four hashes at the beginning of the line.

<details>
  <summary>Template for writing the script for each video:</summary>

Objective statement: It should be a single or two line statement that describes the goal of the video.

1. (Screen where the video will be recorded): Describe the action to be taken on that screen in as much detail as possible. It may contain <attachments> in a placeholder like format to signify if something may be unclear for the person who is reading and recording the video.
This will be the narration on the video. It will be spoken by the narrator, word for word, to the letter. It needs to be clear, concise, and easy to follow.

2. (Screen where the video will be recorded): In addition to detailing the action as much as possible, we can also add context to help understand the action better. This may include explaining why the action is being taken, what the user should expect to see, or any other relevant information.
This will be the narration on the video. It will be spoken by the narrator, word for word, to the letter. It needs to be clear, concise, and easy to follow.
</details>

<details>
  <summary>Outline for learning path of Member role</summary>
  
- User is invited to the workspace and they sign up.
- User after signing up, lands on the Project Page.
- User is introduced to Roles and role permissions.
- General Workflow is outlined (Cases → Results → Defects)
- Importing test cases from other tools
- Repository Management
- Custom/System Fields
- Parameters
- Integrations: Linking external issues with test cases.
- Test plans and Test runs
    - Test runs wizard
    - Bulk Actions
    - Assignment
    - Test run settings
    - Linking external issues with test runs
- Defects management
    - Filing a defect for a result, from a test run.
    - Defects list
    - Linking external issues with defects.
    - Filing external issues directly from a test run.
- Dashboard: track your efforts
- Other Integrations & API
</details>

---

> We need to cover all the permissions of the QA Member role in this learning path.

## User is invited to the workspace and they sign up.

#### (103) What is a workspace?
> Discuss the difference between account and workspace. Each account is uniquely identified by email. Each user can be part of multiple workspaces. Explain the concept of ownership.

#### (104) Joining your workspace

#### (xx) Sign up process when teams use SSO and SCIM

#### (104) Accidental signup?
> User accidentally signs up for a new workspace instead of joining their company workspace.

---

## User after signing up, lands on the Project Page.
> This will be a dedicated video for this role introducing workspace options, navigation, and capabilities of the platform.

#### (68) Qase UI: A guided tour!
#### (68) Finding your way around the workspace
#### (xx) Make Qase Yours: Theme, Profile & Personal Touch

> Introduce the Help Center at this stage. Because, they'll want to know where to find help if they need it.

#### (xx) Help is just a click away!

---

## Introduction to Roles

> Introduce users to Roles and role permissions. Explain who can do what within the workspace.


#### (106) Who's Who in Your Workspace?
#### (107) What's my role?

---

## General Workflow (Cases → Results → Defects)

> Introduce the general workflow of a QA Member in Qase, which involves creating test cases, executing them, and filing defects.

#### (83) What's a project?
#### (109) Organizing with test suites
#### (110) Creating (quick) test cases
#### (111) Anatomy of a test case
#### (112) Executing your tests
#### (113) Filing your first defect

---

## Repository Management

> User now understands basics and wants to learn about repository management. Use the "Task Tides" project** (theme: task management productivity app). In the asset, introduce the tools covered in the following videos, along with the theme. Keep this section very short.

#### (114) Repository management: TASKTIDES
> In this module, we will introduce all the upcoming learning materials—such as code files, diagrams, and other assets—that you can expect as we move forward. Additionally, we’ll introduce our example project, Task Tides: an imaginary productivity and task management application. Throughout the series, we’ll use Task Tides to demonstrate key features and provide a consistent theme for our videos.

#### (115) Repository: tree vs folder view
> Large repositories benefit from folder view for quicker loading times
  
#### (116) Bulk deletion in the repository
> Demonstrate how suite deletion is different from case deletion and a caution about deleting suites with cases.

#### (117) Search and Filters
> Mention shortcut about CFS - Cases, Filters, and Suites.
  
#### (89) Trash bin


> The following assets will cover importing process for teams migrating from other tools, or a spreadsheet software.

#### (39) Qase CSV - old format
#### (38) Qase CSV - custom fields
#### (13) Qase CSV - bulk update
#### (12) Qase CSV - suites
#### (11) Qase CSV - fields
#### (10) Qase CSV - steps
#### (9) Qase CSV - introduction
  

#### (86) Save time with Shared steps
> Explain, demo, and provide details
  

#### (119) Submitting a case for review
> This is for self and manager review

#### (118) Peer Reviews

#### (120) Using AI to generate test cases
> Demonstrate test case generation using copy-paste text.

#### (99) Workspace - tags

#### (81) Project - archive/delete
#### (80) Project settings - access control

#### (19) Understanding the automation status field

#### (78) Project - overview

#### (77) User group - create
#### (87) Groups - view and edit
#### (88) Groups - delete

#### (96) Milestone
#### (67) Test case - mute
#### Test Plans and Test Runs (Optional/Reference)
#### (76) Test plan - edit
#### (75) Test plan - delete
#### (74) Test plan - export
#### (72) Test plan - create manual run
#### (71) Test plan - Create
#### (70) Users - Invite

## Defects and Integration

#### (54) Defect - link/create external issue
#### (53) Defect - export
#### (51) Defect - create

## Test run settings: Explained

#### (63) Test run - link external issue
#### (62) Test run - assignment
#### (61) Test run - defects tab
#### (60) Test run - team stats tab
#### (59) Test run - starting a test run
#### (52) Test run - share report
#### (49) Test run settings - auto complete
#### (48) Test run settings - allow add results to completed test runs
#### (46) Test run settings - fail case on step fail
#### (44) Test run settings - assignee result lock
#### (35) Test run settings - default create/attach defect checkbox
#### (33) Test run settings - fast pass
#### (8) Test run settings - auto assignee
#### (1) Test run settings - autopass


## Other Integrations & API
#### (18) Github - qase-run-link
#### (7) API - attachments
#### (5) API - intro
#### (14) Token - user vs app difference

## Custom/System Fields
#### (28) Custom fields - distribution widget
#### (27) System fields - results status
#### (26) Custom fields - QQL
#### (25) Custom fields - API
#### (23) Custom fields - order
#### (22) Custom fields - create

#### (21) System fields - modify values on paid plans

## Billing and Invoices

#### (69) Billing - invoices
#### Invite/Access Issues & Help
#### (30) Issue - this invite is for another user
