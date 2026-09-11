Rất có thể trong tương lai, Identity and Access Bounded Context (Ngữ cảnh Giới hạn Định danh và Truy cập) sẽ mang diện mạo rất khác so với thiết kế nhúng trực tiếp cơ chế bảo mật và phân quyền ban đầu. Việc thiết kế hướng tới khả năng tái sử dụng (reuse) sẽ buộc đội ngũ phải tập trung vào một mô hình mang tính tổng quát hơn, có thể được khai thác bởi nhiều ứng dụng khác nhau khi cần thiết. Đội ngũ chuyên trách đó — một đội ngũ tách biệt với nhóm Collaboration Context (Ngữ cảnh Cộng tác), nhưng được thành lập từ một vài thành viên của nhóm này — cũng có thể đưa vào nhiều chiến lược triển khai khác nhau. Các chiến lược đó có thể bao gồm việc sử dụng các sản phẩm của bên thứ ba và các giải pháp tích hợp tùy biến theo từng khách hàng — những điều vốn từng nằm ngoài tầm với do sự hỗn độn của cơ chế bảo mật nhúng sâu trước đây.

Do việc phát triển Segregated Core (Lõi Tách biệt — một mẫu hình chiến lược của DDD) chỉ là một bước đệm tạm thời, chúng ta sẽ không đi quá sâu vào các kết quả đó tại đây. Tóm lại, phương pháp này bao gồm việc chuyển toàn bộ các lớp (classes) bảo mật và phân quyền sang các Modules (Mô-đun) biệt lập, đồng thời yêu cầu các client thuộc Application Services (Dịch vụ Ứng dụng) phải kiểm tra bảo mật và phân quyền thông qua các đối tượng đó trước khi gọi vào Core Domain (Miền Cốt lõi). Điều này đã giải phóng Core Domain, giúp nó chỉ tập trung hiện thực hóa việc cấu thành và các hành vi của các đối tượng mô hình cộng tác. Application Service sẽ đảm nhận trách nhiệm bảo mật và chuyển đổi đối tượng:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000051_e9e8d77141ec5a862f68257b5b286b356bf22ce86e6e48d1abdf2b863c0550a8.png)

```java
public class ForumApplicationService ... {
    ...
    @Transactional
    public Discussion startDiscussion(
            String aTenantId,
            String aUsername,
            String aForumId,
            String aSubject) {

        Tenant tenant = new Tenant(aTenantId);
        ForumId forumId = new ForumId(aForumId);
        Forum forum = this.forum(tenant, forumId);

        if (forum == null) {
            throw new IllegalStateException("Forum does not exist.");
        }

        Author author = this.collaboratorService.authorFrom(
                tenant,
                anAuthorId);

        Discussion newDiscussion = forum.startDiscussion(
                this.forumNavigationService(),
                author,
                aSubject);

        this.discussionRepository.add(newDiscussion);

        return newDiscussion;
    }
    ...
}

```

Kết quả đối với lớp Forum sẽ trông như sau:

```java
public class Forum extends Entity {
    ...
    public Discussion startDiscussionFor(
            ForumNavigationService aForumNavigationService,
            Author anAuthor,
            String aSubject) {

        if (this.isClosed()) {
            throw new IllegalStateException("Forum is closed.");
        }

```

```java
        Discussion discussion = new Discussion(
                this.tenant(),
                this.forumId(),
                aForumNavigationService.nextDiscussionId(),
                anAuthor,
                aSubject);

        DomainEventPublisher
                .instance()
                .publish(new DiscussionStarted(
                        discussion.tenant(),
                        discussion.forumId(),
                        discussion.discussionId(),
                        discussion.subject()));

        return discussion;
    }
    ...
}

```

Cách làm này đã loại bỏ sự nhập nhằng giữa User và Permission, đồng thời định hướng mô hình tập trung nghiêm ngặt vào các nghiệp vụ cộng tác. Xin nhắc lại, đây chưa phải là một kết quả hoàn hảo mĩ mãn, nhưng nó đã chuẩn bị hành trang kỹ lưỡng cho toàn đội ngũ trong các đợt tái cấu trúc (refactoring) tương lai nhằm phân tách và tích hợp các Bounded Contexts (Ngữ cảnh Giới hạn). Cuối cùng, đội ngũ Collaboration Context sẽ loại bỏ hoàn toàn các Modules và kiểu dữ liệu bảo mật, phân quyền ra khỏi Bounded Context của mình để hân hoan tiếp nhận Identity and Access Context mới. Mục tiêu tối hậu của họ — biến cơ chế bảo mật thành một thành phần tập trung và có thể tái sử dụng — giờ đây đã nằm trong tầm tay.

Phải thừa nhận rằng, ban đầu đội ngũ hoàn toàn có thể chọn đi theo hướng ngược lại. Họ có thể đã vi phân hóa các Bounded Contexts (miniaturized Bounded Contexts) bằng cách tạo ra hàng loạt ngữ cảnh tách biệt, dẫn đến việc có tổng cộng mười hoặc nhiều hơn thế — mỗi ngữ cảnh cho một tiện ích cộng tác (chẳng hạn như tách Forum và Calendar thành các mô hình riêng). Điều gì có thể dẫn dắt họ đi theo hướng đó? Vì phần lớn các tiện ích cộng tác không bị ghép nối chặt chẽ với nhau, mỗi tiện ích đều có thể được triển khai dưới dạng một thành phần tự trị (autonomous component). Bằng việc đặt từng tiện ích vào một Bounded Context riêng biệt, nhóm có thể tạo ra khoảng mười đơn vị triển khai tự nhiên. Điều đó đúng, nhưng việc tạo ra mười domain models (mô hình miền) khác nhau là không cần thiết để đạt được các mục tiêu triển khai đó, và nó có thể chỉ làm xói mòn các nguyên lý mô hình hóa của Ubiquitous Language (Ngôn ngữ Chung / Toàn hiện).

Thay vào đó, đội ngũ quyết định giữ mô hình thành một khối thống nhất nhưng tạo ra một file JAR riêng cho từng tiện ích cộng tác. Bằng cách sử dụng cơ chế module hóa Jigsaw (Jigsaw modularization trong Java), họ đã tạo ra một đơn vị triển khai dựa trên phiên bản cho từng tiện ích. Bên cạnh các file JAR cho từng phân vùng cộng tác tự nhiên, họ cũng cần một file JAR dành cho các đối tượng mô hình dùng chung (shared model objects), chẳng hạn như Tenant, Moderator, Author, Participant và các đối tượng khác. Đi theo lộ trình này vừa hỗ trợ phát triển một Ubiquitous Language thống nhất, vừa đáp ứng trọn vẹn các mục tiêu triển khai vốn mang lại nhiều lợi thế về kiến trúc và quản trị ứng dụng.

Với hiểu biết nền tảng này, chúng ta có thể khảo sát xem Identity and Access Context đã được hình thành như thế nào.

## Identity and Access Context (Ngữ cảnh Định danh và Truy cập)

Hầu hết các ứng dụng doanh nghiệp ngày nay đều cần trang bị một số hình thức thành phần bảo mật và phân quyền nhằm đảm bảo rằng những người truy cập hệ thống là những người dùng hợp thức, đồng thời được phân quyền chính xác để thực hiện những tác vụ mà họ dự định làm. Như chúng ta vừa phân tích, cách tiếp cận ngây thơ đối với bảo mật ứng dụng là nhồi nhét người dùng và quyền hạn vào từng hệ thống riêng lẻ, điều này tạo ra hiệu ứng ốc đảo (silo effect - sự phân mảnh biệt lập) trong mọi ứng dụng.

## Triết lý Cao bồi (Cowboy Logic)

* LB:    'Bác chẳng khóa chuồng trại hay tháp ủ ngô gì cả, thế mà chẳng ai thèm trộm ngô của bác à?'
* AJ:    'Chó Tumbleweed nhà tôi lo việc quản lý truy cập rồi. Đó là hiệu ứng ốc đảo silo của riêng tôi đấy.'
* LB:    'Cháu nghĩ là bác chẳng hiểu gì về cuốn sách này rồi.'

> 💡 **Giải thích thêm:** "Silo effect" (hiệu ứng ốc đảo / cát cứ thông tin) là thuật ngữ mượn từ các tháp chứa ngũ cốc (silo) trong nông nghiệp — vốn là những kiến trúc hình trụ đứng kín bưng, biệt lập hoàn toàn với nhau. Trong kiến trúc phần mềm và quản trị tổ chức, thuật ngữ này ám chỉ việc mỗi hệ thống, ứng dụng hay phòng ban hoạt động khép kín, tự quản lý người dùng và dữ liệu của riêng mình mà không có sự liên thông, tích hợp hay chia sẻ với phần còn lại. Ở đây, AJ chơi chữ một cách ngô nghê giữa tháp chứa ngô (silo) ngoài đời thực và việc chú chó Tumbleweed canh gác cửa để tự xưng đó là "hiệu ứng silo", khiến LB phải lắc đầu châm chọc.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Người dùng của một hệ thống không thể dễ dàng liên kết với người dùng của bất kỳ hệ thống nào khác, ngay cả khi nhiều người sử dụng chúng thực chất là cùng một cá nhân. Để ngăn chặn các ốc đảo thông tin mọc lên như nấm trên toàn bộ bức tranh doanh nghiệp, các kiến trúc sư cần phải tập trung hóa cơ chế bảo mật và phân quyền. Điều này được thực hiện bằng cách mua ngoài hoặc tự phát triển một hệ thống quản lý định danh và truy cập (IAM - Identity and Access Management). Con đường được lựa chọn sẽ phụ thuộc rất nhiều vào mức độ tinh vi cần thiết, quỹ thời gian sẵn có và tổng chi phí sở hữu (TCO - Total Cost of Ownership).

Việc khắc phục sự rối rắm về định danh và truy cập trong CollabOvation sẽ là một quy trình gồm nhiều bước. Trước tiên, đội ngũ đã tái cấu trúc bằng mẫu hình Segregated Core [Evans]; hãy xem lại mục "Collaboration Context". Bước đi này phục vụ đúng mục đích đề ra tại thời điểm đó: đảm bảo CollabOvation được gột rửa sạch sẽ khỏi các mối bận tâm về bảo mật và phân quyền. Tuy nhiên, họ nhận định rằng việc quản lý định danh và truy cập cuối cùng phải chiếm giữ một ranh giới ngữ cảnh (context boundary) của riêng nó. Điều đó sẽ đòi hỏi một nỗ lực lớn hơn rất nhiều.

Điều này cấu thành một Bounded Context mới — mang tên Identity and Access Context — và sẽ được các Bounded Contexts khác tiêu thụ thông qua các kỹ thuật tích hợp DDD (Domain-Driven Design - Thiết kế Hướng miền) tiêu chuẩn. Đối với các ngữ cảnh tiêu thụ nó, Identity and Access Context đóng vai trò là một Generic Subdomain (Miền con Chung). Sản phẩm này sẽ được đặt tên là IdOvation.

Như Hình 2.9 mô tả, Identity and Access Context cung cấp sự hỗ trợ cho các khách thuê bao đa người thuê (multitenant subscribers). Khi phát triển một sản phẩm SaaS (Software as a Service - Phần mềm dưới dạng Dịch vụ), đây là điều hiển nhiên. Mỗi khách thuê (tenant) và mọi đối tượng tài nguyên thuộc quyền sở hữu của một khách thuê nhất định đều sẽ có một định danh hoàn toàn duy nhất, cô lập một cách logic từng khách thuê khỏi tất cả những khách thuê khác. Người dùng hệ thống được đăng ký qua cổng tự phục vụ (self-service) thông qua hình thức chỉ chấp nhận thư mời (by invitation only). Quyền truy cập an toàn được xử lý thông qua một dịch vụ xác thực (authentication service), và mật khẩu luôn được mã hóa ở mức độ cao. Các nhóm người dùng (groups) và các nhóm lồng nhau (nested groups) hỗ trợ quản lý định danh tinh vi trên toàn bộ tổ chức và thu hẹp tới từng đội nhóm nhỏ nhất. Việc truy cập vào các tài nguyên hệ thống được quản lý thông qua các quyền hạn dựa trên vai trò (role-based permissions) đơn giản, thanh lịch nhưng vô cùng mạnh mẽ.

Figure 2.9 Identity and Access Context. Mọi thứ bên trong ranh giới đều nằm đúng ngữ cảnh theo Ubiquitous Language. Có các thành phần khác trong Bounded Context này, một số nằm trong mô hình và một số nằm ở các tầng khác, nhưng chúng không được hiển thị ở đây nhằm đảm bảo tính dễ đọc. Điều tương tự cũng áp dụng cho các thành phần UI và Application Service.

Ở một bước tiến nâng cao hơn, xuyên suốt mô hình, các Domain Events (Sự kiện Miền) (8) được phát hành (publish) khi các hành vi của mô hình tạo ra sự biến đổi trạng thái mang ý nghĩa đặc biệt đối với những bên quan sát các biến cố đó. Những Events này thường được mô hình hóa dưới dạng danh từ kết hợp với động từ ở thì quá khứ, chẳng hạn như TenantProvisioned, UserPasswordChanged, PersonNameChanged, cùng nhiều sự kiện khác.

Chương tiếp theo, "Context Maps", sẽ trình bày cách thức Identity and Access Context được hai Contexts mẫu còn lại tiêu thụ bằng cách sử dụng các mẫu hình tích hợp DDD.

## Agile Project Management Context (Ngữ cảnh Quản lý Dự án Agile)

Các phương pháp phát triển linh hoạt (agile) tinh gọn đã thúc đẩy sự phổ biến mạnh mẽ của nó, đặc biệt là sau sự ra đời của Tuyên ngôn Agile (Agile Manifesto) vào năm 2001. Trong bản tuyên bố tầm nhìn của mình, SaaSOvation đặt ra sáng kiến chiến lược trọng tâm thứ hai là phát triển một ứng dụng quản lý dự án linh hoạt. Dưới đây là diễn biến của câu chuyện . . .

Sau ba quý bán thuê bao CollabOvation thành công, thực hiện các đợt nâng cấp theo kế hoạch với các cải tiến tăng dần dựa trên phản hồi của khách hàng và đạt doanh thu vượt kỳ vọng, kế hoạch phát triển ProjectOvation của công ty chính thức được khởi động. Đây chính là Core Domain mới của họ, và các lập trình viên hàng đầu từ dự án CollabOvation sẽ được điều động sang nhằm tận dụng kinh nghiệm về kiến trúc đa khách thuê SaaS cũng như vốn kinh nghiệm DDD mới tích lũy của họ.

Công cụ này tập trung vào việc quản lý các dự án linh hoạt, sử dụng Scrum làm khung quản lý dự án lặp đi lặp lại và tăng dần (iterative and incremental). ProjectOvation tuân theo mô hình quản lý dự án Scrum truyền thống, bao gồm đầy đủ: product (sản phẩm), product owner (chủ sở hữu sản phẩm), team (đội ngũ), backlog items (hạng mục tồn đọng), planned releases (các đợt phát hành theo kế hoạch) và sprints (các chu kỳ nước rút). Việc ước lượng backlog item được cung cấp thông qua các bộ tính toán giá trị kinh doanh sử dụng phép phân tích chi phí - lợi ích (cost-benefit analysis).

Kế hoạch kinh doanh khởi đầu bằng một tầm nhìn kép. CollabOvation và ProjectOvation sẽ không đi theo những con đường hoàn toàn tách biệt. SaaSOvation và hội đồng quản trị của công ty đã mường tượng ra một sự đổi mới sáng tạo xoay quanh việc gắn kết các công cụ cộng tác vào quy trình phát triển phần mềm agile. Do đó, các tính năng của CollabOvation sẽ được cung cấp dưới dạng một gói bổ sung tùy chọn (optional add-on) cho ProjectOvation. Bởi vì đóng vai trò cung cấp các tính năng bổ trợ, CollabOvation là một Supporting Subdomain (Miền con Hỗ trợ) đối với ProjectOvation. Các chủ sở hữu sản phẩm và thành viên đội ngũ sẽ tương tác trong các cuộc thảo luận về sản phẩm, lập kế hoạch phát hành và kế hoạch sprint, thảo luận về backlog item, chia sẻ lịch biểu và nhiều hoạt động khác. Đã có kế hoạch tương lai về việc tích hợp quản lý tài nguyên doanh nghiệp vào ProjectOvation, nhưng các mục tiêu ban đầu của sản phẩm agile bắt buộc phải được hoàn thành trước tiên.

Các bên liên quan về mặt kỹ thuật ban đầu dự định phát triển các tính năng của ProjectOvation như một phần mở rộng của mô hình CollabOvation bằng cách phân nhánh mã nguồn trên hệ thống quản lý phiên bản (revision control system source branch). Điều đó thực chất sẽ là một sai lầm chết người, dẫu rằng rất điển hình đối với những ai không dành sự chú ý đúng mực cho các Subdomains trong không gian bài toán (problem space) và Bounded Contexts trong không gian giải pháp (solution space) của họ.

May mắn thay, đội ngũ kỹ thuật đã rút ra bài học đắt giá từ những vấn đề ban đầu với Collaboration Context hỗn tạp. Bài học từ trải nghiệm đó đã thuyết phục họ rằng ngay cả việc manh nha bước vào con đường hợp nhất mô hình quản lý dự án agile với mô hình cộng tác cũng sẽ là một sai lầm nghiêm trọng. Giờ đây, các đội ngũ đã bắt đầu tư duy với sự nghiêng hẳn về phía thiết kế chiến lược của DDD.

Hình 2.10 cho thấy rằng nhờ áp dụng tư duy thiết kế chiến lược, đội ngũ ProjectOvation giờ đây đã nhìn nhận các đối tượng sử dụng hệ thống một cách chuẩn xác: họ là Product Owners (Chủ sở hữu Sản phẩm) và Team Members (Thành viên Đội ngũ). Xét cho cùng, đó chính là các vai trò thành viên dự án do những người thực hành Scrum đảm nhận. Người dùng và vai trò được quản lý bên trong Identity and Access Context tách biệt. Bằng cách sử dụng Bounded Context đó, cổng tự phục vụ cho phép người đăng ký thuê bao tự quản lý định danh cá nhân của họ. Các công cụ quản trị cho phép người quản lý, chẳng hạn như chủ sở hữu sản phẩm, chỉ định các thành viên trong nhóm sản phẩm của mình. Khi các vai trò được quản lý chuẩn xác, Product Owners và Team Members có thể được tạo ra đúng nơi chúng thuộc về: bên trong Agile Project Management Context. Phần còn lại trong thiết kế của dự án sẽ được hưởng lợi khi đội ngũ tập trung toàn lực vào việc nắm bắt Ubiquitous Language của mảng quản lý dự án agile vào trong một domain model được trau chuốt cẩn trọng.

Figure 2.10 Agile Project Management Context. Ubiquitous Language của Bounded Context này xoay quanh các sản phẩm, vòng lặp và đợt phát hành linh hoạt dựa trên Scrum. Để đảm bảo tính dễ đọc, một số thành phần, bao gồm cả các thành phần từ UI và Application Services, không được hiển thị tại đây.

Một yêu cầu đặt ra là ProjectOvation phải vận hành như một tập hợp các dịch vụ ứng dụng tự trị (autonomous application services). Nhóm mong muốn giới hạn sự phụ thuộc của ProjectOvation vào các Bounded Contexts khác ở một chu kỳ định kỳ hợp lý, hoặc ít nhất là trong mức độ thực tế nhất có thể. Nói một cách khái quát, ProjectOvation sẽ có khả năng tự hoạt động độc lập, và nếu IdOvation hoặc CollabOvation có ngừng hoạt động vì bất kỳ lý do gì, ProjectOvation vẫn tiếp tục vận hành một cách tự chủ. Đương nhiên, trong trường hợp đó, một số dữ liệu có thể bị lệch pha đồng bộ trong một khoảng thời gian, và thường là một khoảng thời gian rất ngắn, nhưng toàn bộ hệ thống vẫn tiếp tục vận hành bình thường.

## Ngữ cảnh Mang lại cho Mỗi Thuật ngữ một Ý nghĩa Rất Cụ thể (The Context Gives Each Term a Very Specific Meaning)

Một Product (Sản phẩm) trong Scrum có thể chứa nhiều thể hiện BacklogItem mô tả phần mềm đang được xây dựng. Khái niệm này hoàn toàn khác biệt so với các sản phẩm trên một trang thương mại điện tử mà bạn bỏ vào giỏ hàng để mua sắm. Làm sao chúng ta phân biệt được? Đó là nhờ vào Ngữ cảnh (Context). Chúng ta hiểu Product của mình có ý nghĩa gì bởi vì nó nằm trong Agile PM Context. Trong một Online Store Context (Ngữ cảnh Cửa hàng Trực tuyến), Product lại mang một ý nghĩa hoàn toàn khác biệt. Đội ngũ không cần phải đặt tên cho sản phẩm là ScrumProduct chỉ để phân biệt sự khác nhau đó.

Core Domain gồm Product, Backlog Items, Tasks, Sprints và Releases đã có một khởi đầu thuận lợi hơn rất nhiều nhờ vào những kinh nghiệm quý giá tích lũy được từ SaaSOvation. Dẫu vậy, chúng ta vẫn rất quan tâm đến việc xem xét những bài học lớn mà họ đã đúc kết được dọc theo đường dốc học tập đầy chông gai của việc mô hình hóa cẩn trọng các Aggregates (10).

## Tổng kết (Wrap-Up)

Đó quả là một cuộc thảo luận thực sự chuyên sâu về tầm quan trọng của thiết kế chiến lược trong DDD!

* Bạn đã nghiên cứu kỹ lưỡng về Domains, Subdomains và Bounded Contexts.
* Bạn đã khám phá cách thức đánh giá chiến lược hiện trạng toàn cảnh của doanh nghiệp bằng cách sử dụng các phép đánh giá không gian bài toán và không gian giải pháp.
* Bạn đã đi sâu vào các chi tiết về cách sử dụng Bounded Contexts để phân tách các mô hình một cách tường minh theo phương diện ngôn ngữ.
* Bạn đã học được những thành phần nào nằm bên trong Bounded Contexts, cách định cỡ quy mô chuẩn xác cho chúng, và cách xây dựng chúng để triển khai thực tế.
* Bạn đã cảm nhận được nỗi đau mà đội ngũ SaaSOvation phải nếm trải trong giai đoạn đầu thiết kế Collaboration Context và cách thức cả nhóm đã nỗ lực vượt qua tình cảnh bế tắc đó.
* Bạn đã chứng kiến sự hình thành của Core Domain hiện tại, Agile Project Management Context — tâm điểm của các ví dụ thiết kế và triển khai xuyên suốt cuốn sách.

Đúng như đã hứa, chương tiếp theo sẽ đi sâu vào Context Mapping (Ánh xạ Ngữ cảnh). Đây là một công cụ mô hình hóa chiến lược thiết yếu cần áp dụng trong các thiết kế. Có thể bạn đã nhận ra rằng chúng ta đã thực hiện một phần việc của Context Mapping ngay trong chương này. Điều đó là không thể tránh khỏi khi chúng ta tiến hành đánh giá các miền khác nhau. Dẫu vậy, chúng ta sẽ đi vào chi tiết hơn rất nhiều ở chương sau.

Trang này được chủ ý để trống

## Chương 3 (Chapter 3)

## Context Maps (Bản đồ Ngữ cảnh)

Dù bạn chọn con đường nào, sẽ luôn có người nói rằng bạn đã sai. Luôn có những khó khăn phát sinh cám dỗ bạn tin rằng những kẻ chỉ trích mình là đúng. Để vạch ra một lộ trình hành động và theo đuổi nó đến cùng đòi hỏi lòng dũng cảm.

-Ralph Waldo Emerson

Context Map của một dự án có thể được biểu đạt theo hai cách. Cách đơn giản hơn là vẽ một biểu đồ trực quan thể hiện các ánh xạ giữa hai hay nhiều Bounded Contexts (2) hiện có. Tuy nhiên, hãy hiểu rằng bạn chỉ đang vẽ một biểu đồ đơn giản về những gì vốn đã tồn tại sẵn. Bản vẽ này minh họa cách thức các Bounded Contexts phần mềm thực tế trong không gian giải pháp (solution space) liên kết với nhau thông qua sự tích hợp. Điều này đồng nghĩa với việc cách biểu đạt Context Maps chi tiết và thực chất hơn chính là việc triển khai mã nguồn thực tế của các mối tích hợp đó. Chúng ta sẽ xem xét cả hai cách trong chương này, nhưng để nắm bắt phần lớn các chi tiết triển khai cụ thể, hãy xem chương Tích hợp các Bounded Contexts (Integrating Bounded Contexts) (13).

Ở mức độ khái quát, hãy luôn ghi nhớ rằng chương này tập trung vào việc đánh giá không gian giải pháp (solution space assessment), trong khi chương trước đã xử lý khá nhiều về việc đánh giá không gian bài toán (problem space assessment).

## Lộ trình của Chương này (Road Map to This Chapter)

* Hiểu lý do tại sao việc vẽ một Context Map lại mang tính sống còn đối với sự thành công của dự án.
* Nhận thấy việc vẽ một Context Map đầy đủ ý nghĩa có thể đơn giản và dễ dàng đến nhường nào.
* Xem xét các mối quan hệ tổ chức và hệ thống phổ biến cũng như cách thức chúng tác động đến các dự án của bạn.
* Học hỏi từ các đội ngũ của SaaSOvation khi họ tạo ra các Maps để kiểm soát hoàn toàn dự án của mình.

## Vì sao Context Maps lại Thiết yếu đến vậy (Why Context Maps Are So Essential)

Khi bắt tay vào một nỗ lực DDD, trước tiên hãy vẽ một Context Map trực quan về tình hình dự án hiện tại của bạn. Hãy tạo ra một Context Map mô tả các Bounded Contexts hiện đang liên quan trong dự án của bạn cùng các mối quan hệ tích hợp giữa chúng. Hình 3.1 mô tả một Context Map trừu tượng. Chúng ta sẽ dần lấp đầy các chi tiết khi tiến bước sâu hơn.

Figure 3.1 Context Map của một Domain trừu tượng. Ba Bounded Contexts cùng các mối quan hệ giữa chúng được phác thảo. Chữ U đại diện cho Upstream (Thượng nguồn) và chữ D đại diện cho Downstream (Hạ nguồn).

Bản vẽ đơn giản này chính là Map của đội ngũ bạn. Các đội ngũ dự án khác có thể tham chiếu tới nó, nhưng họ cũng nên tự tạo ra các Maps của riêng mình nếu họ đang triển khai DDD. Bản đồ của bạn được vẽ ra chủ yếu nhằm cung cấp cho đội ngũ của bạn góc nhìn về không gian giải pháp cần thiết để đi đến thành công. Các đội ngũ khác có thể không sử dụng DDD và/hoặc họ có thể chẳng mảy may quan tâm đến góc nhìn của bạn.

## Ôi Không! Lại Có Thuật ngữ Mới Nữa Rồi! (Oh, No! There's New Terminology!)

Chúng ta đang giới thiệu các khái niệm Big Ball of Mud (Kiến trúc Búi bùn lớn), Customer-Supplier (Khách hàng - Nhà cung cấp), và Conformist (Kẻ phục tùng / Tuân thủ) tại đây. Hãy kiên nhẫn; các khái niệm này cùng với những mối quan hệ tích hợp và đội ngũ khác trong DDD được lưu ý tại đây sẽ được thảo luận chi tiết ở phần sau của chương này.

Ví dụ, khi bạn tích hợp các Bounded Contexts trong một doanh nghiệp lớn, bạn có thể cần phải kết nối với một Big Ball of Mud. Đội ngũ bảo trì khối mã nguồn nguyên khối lầy lội đó có thể không quan tâm dự án của bạn đi theo hướng nào, miễn là bạn tuân thủ đúng API của họ. Vì vậy, họ sẽ không thu được bất kỳ hiểu biết sâu sắc nào từ Map của bạn hay những gì bạn làm với API của họ. Dẫu vậy, Map của bạn bắt buộc phải phản ánh đúng loại mối quan hệ mà bạn đang có với họ, bởi vì nó sẽ mang lại cho nhóm của bạn những hiểu biết thiết yếu và chỉ ra những khu vực mà việc giao tiếp liên nhóm (inter-team communication) mang tính bắt buộc sống còn. Việc nắm giữ sự thấu hiểu đó có thể hỗ trợ rất nhiều cho sự thành công của đội ngũ bạn.

## Phương tiện Giao tiếp (Communications Facility)

Bên cạnh việc cung cấp cho bạn danh mục các hệ thống mà bạn bắt buộc phải tương tác, một Context Map còn đóng vai trò như một chất xúc tác mạnh mẽ cho việc giao tiếp giữa các đội ngũ.

Hãy hình dung điều gì sẽ xảy ra nếu nhóm của bạn đinh ninh rằng đội ngũ bảo trì khối mã nguồn nguyên khối lầy lội kia sẽ cung cấp các API mới mà bạn đang phụ thuộc vào, nhưng họ lại không hề có ý định cung cấp chúng, hoặc thậm chí họ còn chẳng hề hay biết bạn đang nghĩ gì. Nhóm của bạn đang trông chờ vào một mối quan hệ Customer-Supplier với khối bùn lầy đó. Tuy nhiên, đội ngũ quản lý hệ thống cũ, bằng việc chỉ cung cấp những gì họ hiện có, đã vô tình ép nhóm của bạn vào một mối quan hệ Conformist đầy bất ngờ. Tùy thuộc vào việc bạn nhận được tin dữ này muộn đến mức nào trong dự án, mối quan hệ thực tế không nhìn thấy trước này có thể làm chậm tiến độ bàn giao hoặc thậm chí phá hỏng toàn bộ dự án của bạn. Bằng việc vẽ một Context Map ngay từ sớm, bạn sẽ buộc phải suy nghĩ cẩn trọng về các mối quan hệ của mình với tất cả các dự án khác mà bạn đang phụ thuộc vào.

Hãy xác định từng mô hình đang vận hành trong dự án và định nghĩa BOUNDED CONTEXT của nó. . . . Hãy đặt tên cho từng BOUNDED CONTEXT, và biến những tên gọi đó thành một phần của UBIQUITOUS LANGUAGE. Hãy mô tả các điểm tiếp xúc giữa các mô hình, phác thảo cơ chế phiên dịch tường minh cho mọi sự giao tiếp và làm nổi bật bất kỳ sự chia sẻ nào. [Evans, tr. 345]

Khi đội ngũ CollabOvation lần đầu tiên bắt tay vào phát triển mô hình greenfield của mình, lẽ ra họ nên sử dụng một Context Map. Ngay cả khi họ gần như bắt đầu từ con số không, việc tuyên bố rõ các giả định của mình về dự án dưới dạng một tấm Bản đồ sẽ thúc đẩy họ phải tư duy

về các Bounded Contexts tách biệt. Họ vẫn có thể liệt kê các phần tử mô hình hóa quan trọng lên bảng trắng, sau đó gom chúng thành các nhóm thuật ngữ ngôn ngữ có liên quan. Việc đó sẽ buộc họ phải nhận diện các ranh giới ngôn ngữ và tạo ra một Context Map đơn giản. Tuy nhiên, họ thực sự không hiểu về mô hình hóa chiến lược một chút nào. Trước tiên, họ cần phải đạt được một bước đột phá về tư duy mô hình hóa chiến lược. Về sau, họ đã có được phát hiện mang tính sống còn về công cụ cứu rỗi dự án này, và áp dụng nó để thu về những lợi ích thiết thực. Khi dự án Core Domain tiếp theo được triển khai, công cụ này một lần nữa đã mang lại những giá trị vượt trội.

Hãy cùng xem bạn có thể tạo ra một Context Map hữu ích nhanh chóng như thế nào.

## Vẽ Context Maps (Drawing Context Maps)

Một Context Map nắm bắt địa hình thực tế hiện có. Trước hết, bạn nên lập bản đồ cho hiện tại, chứ không phải cho một tương lai tưởng tượng. Nếu bức tranh cảnh quan thay đổi khi dự án hiện tại của bạn tiến triển, bạn hoàn toàn có thể cập nhật Map vào thời điểm đó. Trước tiên, hãy tập trung vào tình hình thực tế hiện tại để bạn có thể hình thành sự hiểu biết rõ ràng về việc mình đang ở đâu và xác định xem cần đi đâu tiếp theo.

Việc tạo ra một Context Map trực quan không nhất thiết phải phức tạp. Lựa chọn đầu tiên của bạn luôn là các sơ đồ vẽ tay nơi bảng trắng và bút dạ xóa được thống trị. Phong cách được sử dụng ở đây rất dễ thích ứng như được minh họa bởi [Brandolini]. Nếu bạn quyết định sử dụng một công cụ phần mềm để ghi lại bản vẽ, hãy đảm bảo giữ cho nó thật phi hình thức và mộc mạc.

Nhìn lại Hình 3.1, tên của các Bounded Contexts chỉ là những phần giữ chỗ (placeholders), và các mối quan hệ tích hợp cũng vậy. Tất cả chúng sẽ là những tên gọi thực tế trong một tấm Bản đồ hữu hình. Các mối quan hệ upstream (thượng nguồn) và downstream (hạ nguồn) được hiển thị rõ ràng, ý nghĩa của chúng sẽ được giải thích ở phần sau của chương.

## Giờ Làm việc với Bảng trắng (Whiteboard Time)

Hãy vẽ một sơ đồ đơn giản về tình hình dự án hiện tại của bạn nhằm truyền đạt ở mức khái quát: ranh giới nằm ở đâu, mối quan hệ giữa các ranh giới và giữa các đội ngũ của chúng, những loại hình tích hợp nào đang tham gia, và các cơ chế phiên dịch cần thiết giữa chúng.

Hãy nhớ rằng phần mềm sẽ hiện thực hóa những gì có trong bản vẽ. Nếu bạn cần thêm thông tin về những gì mình nên vẽ, hãy xem xét các hệ thống mà Bounded Context của bạn đang tích hợp cùng.

Đôi khi chúng ta sẽ muốn phóng to (zoom in) và bổ sung thêm chi tiết cho một phần cụ thể của Context Map. Đó chỉ đơn thuần là một góc nhìn khác về cùng một (hoặc nhiều) Context đó. Bên cạnh các ranh giới, mối quan hệ và cơ chế phiên dịch, chúng ta có thể muốn đưa vào các mục khác như Modules (9), các Aggregates (10) quan trọng, cách thức phân bổ nhân sự các nhóm, và bất kỳ thông tin nào khác có liên quan đến các Contexts. Những kỹ thuật này sẽ được chứng minh ở phần sau của chương.

Tất cả các bản vẽ và bất kỳ văn bản giải thích nào đều có thể được tập hợp vào một tài liệu tham khảo duy nhất nếu nó mang lại giá trị cho cả nhóm. Với bất kỳ nỗ lực nào như vậy, chúng ta nên tránh sự rườm rà mang tính nghi thức và duy trì sự đơn giản kết hợp cùng tính linh hoạt (agile). Càng thêm vào nhiều nghi thức hình thức, sẽ càng có ít người muốn sử dụng Map. Việc nhồi nhét quá nhiều chi tiết vụn vặt vào các biểu đồ sẽ không thực sự giúp ích cho nhóm. Giao tiếp cởi mở mới là chìa khóa. Khi các cuộc trò chuyện hé lộ những hiểu biết chiến lược sâu sắc, hãy bổ sung chúng vào Context Map.

## Không, Nó Không Mang Tính Bệnh Doanh nghiệp (No, It's Not Enterprisy)

Một Context Map không phải là một sơ đồ Kiến trúc Doanh nghiệp (Enterprise Architecture) hay sơ đồ cấu trúc liên kết hệ thống (system topology diagram).

> 💡 **Giải thích thêm:** "Enterprisy" (mang phong cách cồng kềnh kiểu doanh nghiệp lớn) là một tiếng lóng kỹ thuật mang sắc thái châm biếm, chỉ những thứ bị làm cho phức tạp hóa quá mức cần thiết, rườm rà, quan liêu, nặng tính nghi thức và cồng kềnh (over-engineered) — tương tự như các tài liệu kiến trúc doanh nghiệp vẽ hàng trăm hộp kết nối trừu tượng nhưng vô dụng đối với việc viết mã thực tế. Context Map của DDD ngược lại hoàn toàn: nó tập trung vào mối quan hệ thực tế giữa các mô hình và đội ngũ, mang tính thực dụng và tinh gọn.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Một Context Map không phải là một sơ đồ Kiến trúc Doanh nghiệp hay sơ đồ cấu trúc liên kết hệ thống. Thông tin được truyền tải dựa trên sự tương tác giữa các mô hình và các mẫu hình tổ chức của DDD. Dẫu vậy, Context Maps vẫn có thể được sử dụng trong các cuộc điều tra kiến trúc cấp cao, mang lại những góc nhìn về doanh nghiệp mà bình thường không thể có được. Chúng có thể làm nổi bật các khiếm khuyết kiến trúc như các điểm nghẽn tích hợp (integration bottlenecks). Bởi vì chúng phản ánh một động lực mang tính tổ chức, Context Maps thậm chí có thể giúp chúng ta nhận diện các vấn đề quản trị hóc búa có nguy cơ cản trở tiến độ, cùng các thách thức khác về đội ngũ và quản lý vốn rất khó phát hiện nếu sử dụng các phương pháp khác.

## Triết lý Cao bồi (Cowboy Logic)

* AJ:    'Nhà tôi bảo: "Tôi ra đồng cỏ với mấy con bò; anh chẳng để ý thấy tôi à?" Tôi bảo: "Không." Thế là bà ấy giận, không thèm nói chuyện với tôi suốt cả tuần.'

Các biểu đồ xứng đáng được dán ở vị trí nổi bật trên bức tường trong khu vực làm việc của nhóm. Nếu nhóm thường xuyên sử dụng wiki, các biểu đồ cũng có thể được tải lên đó. Nhưng nếu trang wiki gần như bị ngó lơ, đừng mất công làm gì. Người ta vẫn thường nói rằng wiki có thể là nơi chôn vùi thông tin ("where information goes to die"). Bất kể chúng được hiển thị ở đâu, Context Maps sẽ bị rơi vào tình trạng "vô hình giữa ban ngày" (hidden in plain sight) trừ khi nhóm thường xuyên dành sự chú ý cho chúng thông qua các cuộc thảo luận thực chất và có ý nghĩa.

## Các Dự án và Mối quan hệ Tổ chức (Projects and Organizational Relationships)

Xin được nhắc lại ngắn gọn, SaaSOvation đang trên lộ trình phát triển và hoàn thiện ba sản phẩm:

1. Một sản phẩm bộ ứng dụng cộng tác xã hội, CollabOvation, cho phép người dùng đã đăng ký xuất bản các nội dung mang giá trị kinh doanh thông qua các công cụ nền web phổ biến như diễn đàn, lịch chia sẻ, blog, wiki và các công cụ tương tự. Đây là sản phẩm chủ lực của SaaSOvation và từng là Core Domain (2) đầu tiên của công ty (mặc dù khi đó nhóm chưa biết đến thuật ngữ DDD). Đây chính là Context mà từ đó mô hình của IdOvation (mục 2) cuối cùng đã được bóc tách ra. CollabOvation hiện sử dụng IdOvation như một Generic Subdomain (2). Bản thân CollabOvation sẽ được tiêu thụ như một Supporting Subdomain (2), đóng vai trò là một gói bổ sung tùy chọn cho ProjectOvation (mục 3).
2. Một mô hình quản trị định danh và truy cập có thể tái sử dụng, IdOvation cung cấp cơ chế quản lý truy cập an toàn dựa trên vai trò cho những người dùng đã đăng ký. Những tính năng này thoạt đầu được tích hợp chung trong CollabOvation (mục 1), nhưng cách triển khai đó bị hạn chế và không thể tái sử dụng. SaaSOvation đã tái cấu trúc CollabOvation, giới thiệu một Bounded Context mới, sạch sẽ. Một tính năng sản phẩm then chốt là

sự hỗ trợ đa khách thuê (multitenancy), điều mang tính sống còn đối với một ứng dụng SaaS. IdOvation đóng vai trò là một Generic Subdomain phục vụ cho các mô hình tiêu thụ nó.

3. Một sản phẩm quản lý dự án linh hoạt, ProjectOvation, tại thời điểm này chính là Core Domain mới. Người dùng của sản phẩm SaaS này có thể tạo ra các tài nguyên quản lý dự án, cũng như các tạo tác phân tích và thiết kế, đồng thời theo dõi tiến độ công việc bằng cách sử dụng khung thực thi dựa trên Scrum. Tương tự như CollabOvation, ProjectOvation sử dụng IdOvation như một Generic Subdomain. Một trong những tính năng mang tính đổi mới sáng tạo là bổ sung sự cộng tác nhóm (mục 1) vào việc quản lý dự án agile, cho phép thảo luận xung quanh các sản phẩm Scrum, các đợt phát hành, các sprint và từng backlog item riêng lẻ.

## Cuối cùng Cũng Đến các Định nghĩa! (Finally, the Definitions!)

Các mẫu hình tổ chức và tích hợp đã đề cập trước đó được định nghĩa như sau . . .

Đâu là các mối quan hệ giữa các Bounded Contexts này và các đội ngũ dự án riêng lẻ của chúng? Có một số mẫu hình tổ chức và tích hợp trong DDD, một trong số đó thường tồn tại giữa bất kỳ hai Bounded Contexts nào. Mỗi định nghĩa sau đây phần lớn được trích dẫn từ [Evans, Ref]:

* Partnership (Quan hệ Đối tác): Khi các đội ngũ trong hai Contexts cùng chung số phận thành công hay thất bại cùng nhau, một mối quan hệ hợp tác cần phải xuất hiện. Các nhóm thiết lập một quy trình phối hợp lập kế hoạch phát triển và cùng nhau quản lý việc tích hợp. Các nhóm phải hợp tác trong quá trình tiến hóa các giao diện của họ để đáp ứng nhu cầu phát triển của cả hai hệ thống. Các tính năng phụ thuộc lẫn nhau nên được lên lịch trình sao cho chúng được hoàn thành trong cùng một đợt phát hành.
* Shared Kernel (Hạt nhân Chia sẻ): Việc chia sẻ một phần của mô hình và mã nguồn liên quan tạo ra một sự phụ thuộc lẫn nhau hết sức mật thiết, điều này có thể nâng tầm công sức thiết kế nhưng cũng có thể làm xói mòn nó. Hãy chỉ định một ranh giới tường minh cho một tập con của domain model mà các nhóm đồng thuận chia sẻ cùng nhau. Hãy giữ cho phần hạt nhân (kernel) này thật nhỏ gọn. Phần nội dung chia sẻ tường minh này có vị thế đặc biệt và không được phép thay đổi nếu không có sự tham vấn với nhóm còn lại. Hãy định nghĩa một quy trình tích hợp liên tục (CI - Continuous Integration) để giữ cho mô hình hạt nhân luôn chặt chẽ và đồng bộ Ubiquitous Language (1) của các nhóm.
* Customer-Supplier Development (Phát triển kiểu Khách hàng - Nhà cung cấp): Khi hai nhóm ở trong mối quan hệ thượng nguồn - hạ nguồn (upstream-downstream relationship), nơi mà nhóm thượng nguồn có thể thành công độc lập với số phận của nhóm hạ nguồn, các nhu cầu của nhóm hạ nguồn sẽ được giải quyết theo nhiều cách khác nhau với hàng loạt hệ quả đa dạng. Các ưu tiên của hạ nguồn sẽ được đưa vào kế hoạch của thượng nguồn. Hãy đàm phán và phân bổ ngân sách tác vụ cho các yêu cầu của hạ nguồn để tất cả mọi người đều hiểu rõ cam kết và tiến độ thời gian.
* Conformist (Kẻ phục tùng / Tuân thủ): Khi hai đội ngũ phát triển có mối quan hệ thượng nguồn / hạ nguồn, trong đó nhóm thượng nguồn không có bất kỳ động lực nào để đáp ứng các nhu cầu của nhóm hạ nguồn, nhóm hạ nguồn sẽ rơi vào thế hoàn toàn bất lực. Lòng vị tha có thể thúc đẩy các lập trình viên thượng nguồn đưa ra những lời hứa hẹn, nhưng chúng rất khó có khả năng được thực hiện. Nhóm hạ nguồn sẽ triệt tiêu độ phức tạp của việc phiên dịch giữa các Bounded Contexts bằng cách tuân thủ một cách mù quáng theo mô hình của nhóm thượng nguồn.
* Anticorruption Layer (Tầng Chống suy thoái / ACL): Các tầng phiên dịch có thể đơn giản, thậm chí thanh lịch, khi bắc cầu nối giữa các Bounded Contexts được thiết kế tốt với các đội ngũ có tinh thần hợp tác. Nhưng khi sự kiểm soát hoặc giao tiếp không đủ tốt để tạo dựng một mối quan hệ Shared Kernel, Partner hay Customer-Supplier, việc phiên dịch sẽ trở nên phức tạp hơn rất nhiều. Tầng phiên dịch lúc này sẽ mang sắc thái phòng thủ rõ nét hơn. Với tư cách là một client hạ nguồn, hãy tạo ra một tầng cách ly để cung cấp cho hệ thống của bạn các chức năng của hệ thống thượng nguồn dưới dạng chính domain model của bạn. Tầng này giao tiếp với hệ thống kia thông qua giao diện sẵn có của nó, đòi hỏi rất ít hoặc không cần sửa đổi đối với hệ thống kia. Ở bên trong nội bộ, tầng này sẽ thực hiện việc phiên dịch theo một hoặc cả hai hướng khi cần thiết giữa hai mô hình.
* Open Host Service (Dịch vụ Máy chủ Mở / OHS): Hãy định nghĩa một giao thức cho phép truy cập vào hệ thống con của bạn dưới dạng một tập hợp các dịch vụ. Hãy mở rộng giao thức này để tất cả những ai cần tích hợp với bạn đều có thể sử dụng. Nâng cấp và mở rộng giao thức để xử lý các yêu cầu tích hợp mới, ngoại trừ trường hợp một nhóm đơn lẻ có những nhu cầu mang tính đặc dị (idiosyncratic). Khi đó, hãy sử dụng một bộ phiên dịch dùng một lần (one-off translator) để tăng cường cho giao thức phục vụ trường hợp đặc biệt đó, nhằm giúp giao thức dùng chung luôn giữ được sự đơn giản và mạch lạc.
* Published Language (Ngôn ngữ Công bố / PL): Việc phiên dịch giữa các mô hình của hai Bounded Contexts đòi hỏi một ngôn ngữ chung. Hãy sử dụng một ngôn ngữ chia sẻ được lập tài liệu đầy đủ có thể biểu đạt các thông tin miền cần thiết như một phương tiện giao tiếp chung, thực hiện phiên dịch khi cần thiết sang và ra khỏi ngôn ngữ đó. Published Language thường được kết hợp cùng với Open Host Service.
* Separate Ways (Đường ai nấy đi): Chúng ta bắt buộc phải tàn nhẫn khi định nghĩa các yêu cầu. Nếu hai tập hợp chức năng không có mối quan hệ ý nghĩa nào với nhau, chúng có thể được cắt đứt hoàn toàn khỏi nhau. Việc tích hợp luôn luôn tốn kém, và đôi khi lợi ích thu về lại rất nhỏ nhoi. Hãy tuyên bố một Bounded Context hoàn toàn không có bất kỳ kết nối nào với các ngữ cảnh khác, cho phép các lập trình viên tìm ra các giải pháp chuyên biệt, đơn giản bên trong phạm vi thu hẹp này.
* Big Ball of Mud (Kiến trúc Búi bùn lớn): Khi khảo sát các hệ thống hiện có, chúng ta nhận thấy rằng trên thực tế có những phần của hệ thống, thường là những phần rất lớn, nơi các mô hình bị trộn lẫn hỗn tạp và ranh giới hoàn toàn thiếu nhất quán. Hãy vẽ một ranh giới bao quanh toàn bộ mớ hỗn độn đó và định danh nó là một Big Ball of Mud. Tuyệt đối không cố gắng áp dụng việc mô hình hóa tinh vi bên trong Context này. Hãy luôn cảnh giác cao độ trước xu hướng bành trướng của những hệ thống như vậy sang các Contexts khác.

Bằng cách tích hợp với Identity and Access Context, cả Collaboration Context lẫn Agile Project Management Context đều tránh được việc phải chọn giải pháp Separate Ways đối với vấn đề bảo mật và phân quyền. Đúng là Separate Ways có thể được áp dụng trên toàn Context cho một hệ thống cụ thể, nhưng nó cũng có thể được vận dụng theo từng trường hợp riêng lẻ. Ví dụ, một nhóm có thể từ chối sử dụng hệ thống bảo mật tập trung nhưng vẫn có thể chọn tích hợp với một số tiện ích tiêu chuẩn doanh nghiệp khác.

Các nhóm sẽ hợp tác với nhau theo các vai trò Customer-Supplier. Ban lãnh đạo của SaaSOvation chắc chắn sẽ không bao giờ cho phép một nhóm ép buộc các nhóm khác phải trở thành Conformists. Không phải mối quan hệ Conformist lúc nào cũng tiêu cực. Đúng hơn, Customer-Supplier đòi hỏi sự cam kết từ phía Nhà cung cấp (Supplier) trong việc hỗ trợ cho Khách hàng (Customer), điều này thúc đẩy mối quan hệ liên nhóm tích cực mà SaaSOvation tin rằng họ cần có để đạt được thành công trọn vẹn. Đương nhiên, không phải lúc nào Khách hàng cũng luôn đúng, vì vậy sự nhượng bộ và thỏa hiệp qua lại bắt buộc phải tồn tại. Xét về tổng thể, chính mối quan hệ tổ chức tích cực mới là điều các nhóm cần duy trì.

Các mối tích hợp của các nhóm sẽ tận dụng Open Host Service và Published Language. Có thể gây đôi chút ngạc nhiên là họ cũng sẽ sử dụng cả Anticorruption Layer. Đây không phải là một sự mâu thuẫn, ngay cả khi họ đang thiết lập các tiêu chuẩn mở giữa các Bounded Contexts của mình. Họ vẫn có thể hiện thực hóa các lợi ích của việc phiên dịch biệt lập bằng cách sử dụng các nguyên lý nền tảng của nó trong các Contexts hạ nguồn, nhưng với độ phức tạp ít hơn nhiều so với khi phải tiêu thụ một Big Ball of Mud. Các tầng phiên dịch sẽ rất đơn giản và thanh lịch.

Các bản vẽ Context Map tiếp theo sẽ sử dụng các chữ viết tắt sau để chỉ ra các mẫu hình được áp dụng tại mỗi đầu của một mối quan hệ:

* ACL cho Anticorruption Layer
* OHS cho Open Host Service
* PL cho Published Language

Khi bạn xem xét các Context Maps mẫu và phần văn bản giải thích đi kèm dưới đây, có thể sẽ rất hữu ích nếu bạn liếc nhìn lại Chương 2, "Domains, Subdomains, and Bounded Contexts". Các sơ đồ của từng Bounded Context trong số ba ngữ cảnh mẫu cũng rất hữu ích tại đây. Vì chúng vẫn ở mức độ tương đối khái quát, các sơ đồ đó hoàn toàn có thể được đưa vào làm một phần của Maps cho từng Context, mặc dù chúng không được lặp lại tại đây.

## Lập Bản đồ cho Ba Ngữ cảnh (Mapping the Three Contexts)

Bây giờ hãy cùng bước vào trải nghiệm thực tế của đội ngũ để chúng ta có thể học hỏi từ những gì họ đã làm . . .

Khi đội ngũ CollabOvation nhận ra sự hỗn độn mà họ đã tạo ra, họ đã đào sâu vào cuốn sách [Evans] để tìm lối thoát. Trong số những phát hiện có giá trị to lớn thuộc các mẫu hình thiết kế chiến lược, họ đã tìm thấy một công cụ thực tiễn mang tên Context Maps. Họ cũng tìm thấy một bài viết trực tuyến rất hữu ích của [Brandolini] đào sâu thêm về kỹ thuật này. Vì chỉ dẫn của công cụ này chỉ ra rằng họ nên lập bản đồ địa hình hiện có, đó chính là bước đầu tiên họ thực hiện. Hình 3.2 cho thấy các kết quả thu được.

Tấm Bản đồ đầu tiên do nhóm tạo ra làm nổi bật sự nhận biết ban đầu của họ về sự tồn tại của một Bounded Context mà họ đặt tên là Collaboration Context. Bằng hình dạng kỳ dị của ranh giới hiện có, họ đã truyền tải rất thỏa đáng khả năng tồn tại của một Context thứ hai, nhưng lại là một ngữ cảnh chưa có sự phân tách sạch sẽ và rõ ràng khỏi Core Domain.

Figure 3.2 Sự hỗn độn bên trong Collaboration Context gây ra bởi các khái niệm không mong muốn được vạch trần bởi Map này. Biển báo nguy hiểm chỉ ra khu vực không thuần khiết.

Một lối đi hẹp gần phía trên cùng cho phép các khái niệm ngoại lai di chuyển qua lại gần như không bị kiểm duyệt, đúng như biển báo nguy hiểm chỉ ra. Không phải các ranh giới Context bắt buộc phải hoàn toàn bất khả xâm phạm. Giống như bất kỳ ranh giới nào, nhóm muốn Collaboration Context phải kiểm soát với sự hiểu biết đầy đủ về những gì được phép bước qua biên giới của nó và vì mục đích gì. Nếu không, vùng lãnh thổ sẽ bị xâm lấn bởi những vị khách không rõ danh tính và có thể không được chào đón. Trong trường hợp của một mô hình, những vị khách không mời này thường mang lại sự nhầm lẫn và lỗi bọ (bugs). Những người làm mô hình nên hòa nhã và thậm chí chào đón, nhưng phải dưới những điều kiện ủng hộ trật tự và sự hòa hợp. Bất kỳ khái niệm ngoại lai nào bước vào ranh giới đều phải chứng minh được quyền được hiện diện ở đó, thậm chí phải khoác lên mình những đặc tính tương thích với vùng lãnh thổ bên trong.

Phân tích này không chỉ dẫn đến một sự hiểu biết tốt hơn về tình trạng hiện tại của mô hình, mà còn chỉ ra dự án cần phải đi theo hướng nào. Một khi đội ngũ dự án nhận ra rằng các khái niệm như bảo mật, người dùng và phân quyền không thuộc về bên trong Collaboration Context, họ đã phản ứng một cách tương ứng. Nhóm buộc phải tách biệt những khái niệm này ra khỏi Core Domain và chỉ cho phép chúng bước vào dưới những điều khoản được chấp thuận.

Đây là một cam kết mang tính sống còn của dự án DDD. Ngôn ngữ của từng Bounded Context bắt buộc phải được tôn trọng để mọi mô hình luôn giữ được sự thuần khiết. Sự phân tách ngôn ngữ và việc tuân thủ nghiêm ngặt nó sẽ giúp mỗi đội ngũ tham gia dự án tập trung vào Bounded Context của chính họ và giữ cho tầm nhìn luôn hướng trúng vào công việc của mình.

Việc áp dụng phân tích Subdomain, hay đánh giá không gian bài toán, đã dẫn dắt nhóm tới sơ đồ được minh họa trong Hình 3.3. Hai Subdomains đã được bóc tách ra từ một Bounded Context đơn lẻ. Vì việc căn chỉnh các Subdomains theo tỷ lệ một-đối-một với các Bounded Contexts là một mục tiêu tốt, phân tích này đã chỉ ra sự cần thiết phải chia Bounded Context đơn lẻ này thành hai.

Figure 3.3 Phân tích Subdomain của nhóm đã dẫn đến việc phát hiện ra hai miền: một Collaboration Core Domain và một Security Generic Subdomain.

Phân tích Subdomain và ranh giới đã dẫn đến các quyết định dứt khoát. Khi những người dùng con người của CollabOvation tương tác với các tính năng sẵn có, họ làm điều đó với tư cách là Participants, Authors, Moderators, v.v. Hàng loạt các sự phân tách ngữ cảnh khác sẽ được thảo luận sau, nhưng điều này mang lại một hình dung rõ ràng về các sự phân chia cần thiết đã được tạo ra. Với tri thức đó, các ranh giới rõ ràng và sắc nét được chỉ định trên Context Map cấp cao trong Hình 3.4 đã ra đời. Nhóm đã sử dụng mẫu hình Segregated Core [Evans] để tái cấu trúc nhằm đạt đến điểm sáng tỏ này. Các hình dạng dễ nhận diện của các ranh giới đóng vai trò như các biểu tượng hoặc tín hiệu thị giác cho từng Context. Việc giữ nguyên các hình dạng tương đối qua các sơ đồ khác nhau có thể hỗ trợ rất tốt cho khả năng nhận thức.

Figure 3.4 Core Domain ban đầu được đánh dấu bằng ranh giới đậm và các điểm tích hợp. Tại đây IdOvation đóng vai trò là một Generic Subdomain cho CollabOvation ở hạ nguồn.

Các Context Maps thường không xuất hiện cùng một lúc như các bản phác thảo khác nhau có thể khiến bạn lầm tưởng, mặc dù khi đã thực sự hiểu ra, chúng không hề khó tạo ra. Tư duy và thảo luận giúp tinh chỉnh một Map thông qua các vòng lặp nhanh chóng. Một số cải tiến có thể đến dưới dạng các điểm tích hợp, vốn mô tả các mối quan hệ giữa các Contexts.

Hai tấm Maps đầu tiên chỉ ra những thành quả gặt hái được sau khi áp dụng thiết kế chiến lược. Sau khi dự án CollabOvation ban đầu đã đi đúng hướng, nhóm đã bóc tách thành công các mối bận tâm về định danh và truy cập ra ngoài. Khi tiến triển, họ đã tạo ra Context Map trong Hình 3.4. Nhóm chỉ phác thảo Core Domain, Collaboration Context, cùng với Generic Subdomain mới, Identity and Access Context. Họ không hề vẽ bất kỳ mô hình nào trong tương lai, chẳng hạn như Agile Project Management Context. Việc nhảy cóc quá xa về phía trước sẽ chẳng giúp ích gì cho nhóm. Họ chỉ cần sửa chữa các khiếm khuyết với những gì đang tồn tại. Các biến đổi hỗ trợ các hệ thống sắp tới sẽ sớm trở nên cần thiết, và tấm Map đó thuộc về trách nhiệm của đội ngũ tương lai.

## Giờ Làm việc với Bảng trắng (Whiteboard Time)

* Nghĩ về Bounded Context của chính bạn, bạn có thể nhận diện các khái niệm không thuộc về nó không? Nếu có, hãy vẽ một Context Map mới thể hiện các Contexts mong muốn và mối quan hệ giữa chúng.
* Bạn sẽ chọn mối quan hệ nào trong số chín mối quan hệ tổ chức và tích hợp của DDD, và tại sao?

Khi dự án tiếp theo liên quan đến ProjectOvation bắt đầu khởi động, đã đến lúc mở rộng Map hiện có với Core Domain mới, Agile Project Management Context. Kết quả của đợt lập bản đồ đó được thể hiện trong Hình 3.5. Việc ghi nhận những gì đang nằm trong kế hoạch hoàn toàn không phải là quá sớm —

mặc dù nó chưa hề được chuyển thành mã nguồn. Các chi tiết bên trong Context mới chưa được hiểu tường tận, nhưng điều đó sẽ dần sáng tỏ qua các cuộc thảo luận. Việc áp dụng thiết kế chiến lược cấp cao ở giai đoạn sớm này sẽ giúp tất cả các đội ngũ hiểu rõ trách nhiệm của họ nằm ở đâu. Vì tấm Map thứ ba trong số ba Maps cấp cao chỉ là một sự mở rộng của bản đồ trước đó, chúng ta sẽ tập trung vào nó. Đó chính là nơi SaaSOvation đang hướng tới. Công ty đã chỉ định các lập trình viên trưởng giàu kinh nghiệm cho dự án mới. Là ngữ cảnh phong phú nhất trong số ba Contexts và là định hướng hiện tại, Core Domain mới chính là nơi các lập trình viên giỏi nhất nên cống hiến.

Một số sự phân tách thiết yếu đã được hiểu rất rõ ràng. Tương tự như Collaboration Context, khi người dùng của ProjectOvation tạo sản phẩm, lập kế hoạch phát hành, lên lịch sprint và xử lý các tác vụ của backlog items, họ làm điều đó với tư cách là Product Owners và Team Members. Identity and Access Context được tách biệt hoàn toàn khỏi Core Domain. Điều tương tự cũng diễn ra đối với việc họ sử dụng Collaboration Context. Giờ đây nó là một Supporting Subdomain. Bất kỳ sự tiêu thụ nào của mô hình mới cũng sẽ được bảo vệ bởi các ranh giới và các cơ chế phiên dịch sang các khái niệm của Core Domain.

Hãy xem xét các chi tiết tinh tế hơn của những biểu đồ này. Chúng không phải là các sơ đồ kiến trúc hệ thống. Nếu đúng là như vậy, xét thấy Agile Project Management Context là Core Domain mới của chúng ta, chúng ta sẽ kỳ vọng nó nằm ở trên cùng hoặc ở vị trí trung tâm của biểu đồ. Tuy nhiên, tại đây, nó lại nằm ở dưới cùng. Đặc điểm có vẻ kỳ lạ này đóng vai trò chỉ dẫn trực quan rằng mô hình cốt lõi nằm ở hạ nguồn (downstream) của các mô hình khác.

Figure 3.5 Core Domain hiện tại được đánh dấu bằng ranh giới đậm và các điểm tích hợp. CollabOvation Supporting Subdomain và IdOvation Generic Subdomain nằm ở thượng nguồn.

Nét tinh tế này đóng vai trò như một tín hiệu thị giác khác. Các mô hình thượng nguồn có tầm ảnh hưởng tới các mô hình hạ nguồn, giống như các hoạt động diễn ra ở thượng nguồn một con sông thường có xu hướng tác động tới các quần thể dân cư ở hạ nguồn, dù là tích cực hay tiêu cực. Hãy nghĩ đến các chất ô nhiễm bị một thành phố lớn xả thẳng xuống sông. Những chất ô nhiễm đó có thể ít ảnh hưởng đến chính thành phố đó, nhưng các thành phố ở hạ nguồn có thể phải đối mặt với những hậu quả thảm khốc. Vị trí theo chiều dọc của các mô hình trên biểu đồ giúp nhận diện các ảnh hưởng từ thượng nguồn lên các mô hình hạ nguồn. Các nhãn U (Upstream) và D (Downstream) chỉ rõ điều này giữa từng mô hình liên kết. Những nhãn này khiến việc định vị vị trí theo chiều dọc của từng Context trở nên ít quan trọng hơn, dẫu vậy việc bố trí trực quan như vậy vẫn mang lại tính thẩm mỹ cao.

## Triết lý Cao bồi (Cowboy Logic)

LB:    'Khi cậu thấy khát khô cả họng, hãy luôn uống nước ở phía trên đầu nguồn của đàn bò.'

> 💡 **Giải thích thêm:** "Always drink upstream from the herd" (khi khát, luôn uống nước phía trên đầu nguồn của đàn gia súc) là câu châm ngôn kinh điển của các cao bồi miền Tây. Đàn gia súc lội qua sông sẽ khuấy đục bùn cát và thải chất bẩn xuống nước; do đó kẻ khôn ngoan phải lấy nước ở thượng nguồn (upstream). Trong kiến trúc phần mềm DDD, hệ thống thượng nguồn (Upstream - U) nắm quyền kiểm soát mô hình và giao diện; hệ thống hạ nguồn (Downstream - D) phải hứng chịu mọi thay đổi từ thượng nguồn. Nếu hạ nguồn không muốn bị "ô nhiễm" bởi mô hình của thượng nguồn, nó bắt buộc phải xây dựng Tầng Chống suy thoái (Anticorruption Layer - ACL) để lọc sạch dữ liệu.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Identity and Access Context nằm ở vị trí xa nhất về phía thượng nguồn. Nó tạo ra tác động lên cả Collaboration Context lẫn Agile Project Management Context. Collaboration Context của chúng ta cũng nằm ở thượng nguồn đối với Agile Project Management Context bởi vì mô hình agile phụ thuộc vào mô hình và các dịch vụ cộng tác. Như đã lưu ý trong chương Bounded Contexts (2), ProjectOvation sẽ vận hành một cách tự chủ nhất có thể trong thực tế. Hoạt động của nó bắt buộc phải tiếp diễn phần lớn độc lập với tính sẵn sàng của các hệ thống xung quanh. Điều này không có nghĩa là các dịch vụ tự trị có thể hoạt động hoàn toàn độc lập khỏi các mô hình thượng nguồn. Chúng ta bắt buộc phải thiết kế theo những phương thức giúp hạn chế tối đa các phụ thuộc trực tiếp theo thời gian thực. Dù tự trị, Agile Project Management Context của chúng ta vẫn nằm ở hạ nguồn của các ngữ cảnh khác.

Việc trang bị cho một ứng dụng các dịch vụ tự trị không đồng nghĩa với việc các cơ sở dữ liệu từ các Contexts thượng nguồn chỉ đơn thuần được sao chép (replicated) sang Context phụ thuộc. Sự sao chép dữ liệu sẽ buộc hệ thống cục bộ phải gánh vác nhiều trách nhiệm không mong muốn. Điều đó sẽ đòi hỏi phải tạo ra một Shared Kernel, thứ vốn không thực sự mang lại sự tự trị đích thực.

Trên tấm Map mới nhất, hãy chú ý các hộp kết nối ở phía thượng nguồn của mỗi kết nối. Cả hai hộp kết nối đều được gắn nhãn OHS/PL, chữ viết tắt nhận diện Open Host Service (Dịch vụ Máy chủ Mở) và Published Language (Ngôn ngữ Công bố). Cả ba hộp kết nối ở phía hạ nguồn đều được gắn nhãn ACL, chữ viết tắt của Anticorruption Layer (Tầng Chống suy thoái). Các cách triển khai kỹ thuật cụ thể được trình bày trong chương Tích hợp các Bounded Contexts (Integrating Bounded Contexts) (13). Tóm lại, các mẫu hình tích hợp này có các đặc tính kỹ thuật sau:

* Open Host Service: Mẫu hình này có thể được triển khai dưới dạng các tài nguyên dựa trên REST mà các client Bounded Contexts tương tác cùng. Chúng ta thường nghĩ Open Host Service như một API gọi thủ tục từ xa (RPC - Remote Procedure Call), nhưng nó hoàn toàn có thể được triển khai bằng cơ chế trao đổi thông điệp (message exchange).
* Published Language: Điều này có thể được triển khai theo một vài cách khác nhau nhưng thường được thực hiện dưới dạng một lược đồ XML (XML schema). Khi được thể hiện với các dịch vụ dựa trên REST, Published Language được kết xuất dưới dạng các biểu diễn (representations) của các khái niệm miền. Các biểu diễn có thể bao gồm cả XML và JSON, ví dụ như vậy. Người ta cũng hoàn toàn có thể kết xuất các biểu diễn dưới dạng Google Protocol Buffers. Nếu bạn đang xuất bản các giao diện người dùng Web, nó cũng có thể bao gồm các biểu diễn HTML. Một lợi thế của việc sử dụng REST là mỗi client có thể chỉ định Published Language ưu tiên của mình, và các tài nguyên sẽ kết xuất các biểu diễn theo đúng kiểu nội dung (content type) được yêu cầu. REST cũng có lợi thế trong việc tạo ra các biểu diễn siêu phương tiện (hypermedia representations), tạo điều kiện thuận lợi cho HATEOAS (Hypermedia as the Engine of Application State - Siêu phương tiện đóng vai trò động cơ điều hướng trạng thái ứng dụng). Siêu phương tiện làm cho Published Language trở nên vô cùng năng động và có tính tương tác cao, cho phép các client điều hướng đến các tập hợp tài nguyên được liên kết. Ngôn ngữ có thể được xuất bản bằng cách sử dụng các kiểu phương tiện (media types) tiêu chuẩn và/hoặc tùy biến. Published Language cũng được sử dụng trong một Event-Driven Architecture (Kiến trúc Hướng sự kiện) (4), nơi các Domain Events (8) được chuyển phát dưới dạng các thông điệp tới các bên quan tâm đã đăng ký.
* Anticorruption Layer: Một Domain Service (Dịch vụ Miền) (7) có thể được định nghĩa trong Context hạ nguồn cho từng loại Anticorruption Layer. Bạn cũng có thể đặt một Anticorruption Layer đằng sau một giao diện Repository (Kho lưu trữ) (12). Nếu sử dụng REST, một hiện thực hóa Domain Service phía client sẽ truy cập vào một Open Host Service từ xa. Các phản hồi của máy chủ tạo ra các biểu diễn dưới dạng một Published Language. Tầng Anticorruption Layer ở hạ nguồn sẽ phiên dịch các biểu diễn này thành các đối tượng miền của chính Context cục bộ của nó. Đây chính là nơi mà, ví dụ, Collaboration Context yêu cầu Identity and Access Context cung cấp một tài nguyên User-trong-vai-trò-Moderator. Nó có thể nhận được tài nguyên được yêu cầu dưới dạng XML hoặc JSON, rồi sau đó phiên dịch thành một Moderator — vốn là một Value Object. Thể hiện Moderator mới này phản ánh một khái niệm theo các thuật ngữ của mô hình hạ nguồn, chứ không phải mô hình thượng nguồn.

Các mẫu hình được lựa chọn đều là những mẫu hình phổ biến. Việc giới hạn các lựa chọn giúp giữ cho phạm vi tích hợp được thảo luận trong cuốn sách này ở mức có thể kiểm soát được. Chúng ta sẽ thấy, ngay cả giữa số ít các mẫu hình được chọn lọc này, vẫn có sự đa dạng lớn trong cách thức áp dụng chúng vào thực tế.

Câu hỏi vẫn còn đó: Liệu đó có phải là tất cả những gì cần có để tạo ra một Context Map? Có thể. Góc nhìn cấp cao mang lại một lượng tri thức rất tốt về toàn bộ dự án nói chung. Dẫu vậy, chúng ta có thể tò mò về những gì thực sự diễn ra bên trong các kết nối và các mối quan hệ được định danh trên từng Context. Sự tò mò giữa các thành viên trong nhóm thôi thúc chúng ta tạo ra nhiều chi tiết hơn một chút. Khi chúng ta phóng to vào bên trong, bức tranh có phần mờ ảo về ba mẫu hình tích hợp sẽ trở nên sắc nét và rõ ràng hơn bao giờ hết.